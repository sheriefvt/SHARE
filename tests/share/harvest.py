import random
import math
from faker import Factory
import threading
import pytest
import datetime
from share.models import HarvestLog
from share.models import SourceConfig
from share.models import SourceUniqueIdentifier
from django.db import DatabaseError
from share.models import RawDatum
from share.harvest import BaseHarvester
from share.tasks import HarvesterTask
from unittest import mock

from django.db import transaction
from django.conf import settings

from share.harvest.exceptions import HarvesterConcurrencyError, HarvesterDisabledError

from tests.share import factories


@pytest.fixture
def source_config():
    source_config = factories.SourceConfigFactory()

    class MockHarvester(BaseHarvester):
        KEY = source_config.harvester.key
        VERSION = '0.0.0'

        do_harvest = mock.Mock()
        _rawdata = []

    def do_harvest(*args, **kwargs):
        for i in MockHarvester._rawdata:
            yield i
    source_config.harvester.get_class().do_harvest.side_effect = do_harvest

    return source_config


@pytest.fixture
def committed_source_config(transactional_db):
    source_config = factories.SourceConfigFactory()

    class MockHarvester(BaseHarvester):
        KEY = source_config.harvester.key
        VERSION = '0.0.0'

        do_harvest = mock.Mock()
        _rawdata = []

    def do_harvest(*args, **kwargs):
        for i in MockHarvester._rawdata:
            yield i
    source_config.harvester.get_class().do_harvest.side_effect = do_harvest

    return source_config


class SyncedThread(threading.Thread):

    def __init__(self, target, args=(), kwargs={}):
        self._end = threading.Event()
        self._start = threading.Event()

        def _target():
            with transaction.atomic(using='locking'):
                target()
                self._start.set()
                self._end.wait(1)

        super().__init__(target=_target, args=args, kwargs=kwargs)

    def start(self):
        super().start()
        self._start.wait()

    def join(self, timeout=1):
        self._end.set()
        return super().join(timeout)


def harvest(*args, **kwargs):
    # Set retries to be really high to avoid retrying
    return HarvesterTask().apply(args, kwargs, retries=999)


@pytest.mark.django_db
class TestHarvestTask:

    def test_errors_on_locked(self, committed_source_config):
        t = SyncedThread(committed_source_config.acquire_lock)
        t.start()

        with pytest.raises(HarvesterConcurrencyError):
            harvest(committed_source_config.source.user.id, committed_source_config.label)

        t.join()

        assert HarvestLog.objects.filter(status=HarvestLog.STATUS.rescheduled).count() == 1

    def test_force_ignores_lock_error(self, committed_source_config):
        t = SyncedThread(committed_source_config.acquire_lock)
        t.start()

        harvest(committed_source_config.source.user.id, committed_source_config.label, force=True)

        t.join()

    def test_harvester_disabled(self, source_config):
        source_config.disabled = True
        source_config.save()
        with pytest.raises(HarvesterDisabledError):
            harvest(source_config.source.user.id, source_config.label)

    def test_harvester_disabled_force(self, source_config):
        source_config.disabled = True
        source_config.save()
        harvest(source_config.source.user.id, source_config.label, force=True)

    def test_harvester_disabled_ignore(self, source_config):
        source_config.disabled = True
        source_config.save()
        harvest(source_config.source.user.id, source_config.label, ignore_disabled=True)

    def test_harvest_fails(self, source_config):
        source_config.harvester.get_class().do_harvest.side_effect = ValueError('In a test')
        with pytest.raises(ValueError) as e:
            harvest(source_config.source.user.id, source_config.label)

        log = HarvestLog.objects.get(source_config=source_config)

        assert e.value.args == ('In a test', )
        assert log.status == HarvestLog.STATUS.failed
        assert log.completions == 0
        assert 'ValueError: In a test' in log.error

    def test_harvest_database_error(self, source_config):
        def do_harvest(*args, **kwargs):
            yield ('doc1', b'doc1data')
            yield ('doc2', b'doc2data')
            yield ('doc3', b'doc3data')
            raise DatabaseError('In a test')
        source_config.harvester.get_class().do_harvest.side_effect = do_harvest

        with pytest.raises(DatabaseError) as e:
            harvest(source_config.source.user.id, source_config.label)

        log = HarvestLog.objects.get(source_config=source_config)

        assert log.raw_data.count() == 0
        assert e.value.args == ('In a test', )
        assert log.status == HarvestLog.STATUS.failed
        assert log.completions == 0
        assert 'DatabaseError: In a test' in log.error

    def test_partial_harvest_fails(self, source_config):
        def do_harvest(*args, **kwargs):
            yield ('doc1', b'doc1data')
            yield ('doc2', b'doc2data')
            yield ('doc3', b'doc3data')
            raise ValueError('In a test')
        source_config.harvester.get_class().do_harvest.side_effect = do_harvest

        with pytest.raises(ValueError) as e:
            harvest(source_config.source.user.id, source_config.label)

        log = HarvestLog.objects.get(source_config=source_config)

        assert log.raw_data.count() == 3
        assert e.value.args == ('In a test', )
        assert log.status == HarvestLog.STATUS.failed
        assert log.completions == 0
        assert 'ValueError: In a test' in log.error

    def test_log_links_does_not_shadow_original(self, source_config):
        pass

    def test_failed_linking_rollsback(self, source_config):
        pass

    def test_force_always_works(self, source_config):
        pass

    def test_log_values(self, source_config):
        harvest(source_config.source.user.id, source_config.label)
        log = HarvestLog.objects.get(source_config=source_config)

        assert log.task_id is not None
        assert log.status == HarvestLog.STATUS.succeeded
        assert log.error == ''
        assert log.completions == 1
        assert log.start_date.date() == datetime.date.today() - datetime.timedelta(days=1)
        assert log.end_date.date() == datetime.date.today()
        assert log.source_config == source_config
        assert log.share_version == settings.VERSION
        assert log.harvester_version == source_config.get_harvester().VERSION
        assert log.source_config_version == source_config.version

    def test_laziness(self, source_config):
        pass

    def test_superfluous(self, source_config):
        pass

    def test_limit(self, source_config):
        pass

    @pytest.mark.parametrize('count, rediscovered, superfluous, limit, ingest', {
        (count, int(rediscovered), False, int(limit) if limit is not None else None, True)
        for count in (0, 1, 500, 501, 1010)
        for limit in (None, 0, 1, count * .5, count, count * 2)
        for rediscovered in (0, 1, count * .5, count)
        if rediscovered <= count
    } | {
        (count, int(rediscovered), superfluous, None, ingest)
        for count in (0, 150)
        for ingest in (True, False)
        for superfluous in (True, False)
        for rediscovered in (0, count * .5, count)
        if rediscovered <= count
    })
    def test_data_flow(self, source_config, monkeypatch, count, rediscovered, superfluous, limit, ingest, django_assert_num_queries):
        assert rediscovered <= count, 'Y tho'

        fake = Factory.create()
        mock_ingest_task = mock.Mock()

        monkeypatch.setattr('share.tasks.IngestTask', mock_ingest_task)
        source_config.harvester.get_class()._rawdata = [(fake.sentence(), fake.binary(750)) for _ in range(count)]
        list(RawDatum.objects.store_chunk(source_config, random.sample(source_config.harvester.get_class()._rawdata, rediscovered)))

        # TODO Drop this number....
        with django_assert_num_queries(15 + math.ceil((count if limit is None or count < limit else limit) / 500) * 3):
            harvest(source_config.source.user.id, source_config.label, superfluous=superfluous, limit=limit, ingest=ingest)

        log = HarvestLog.objects.get(source_config=source_config)

        assert log.completions == 1
        assert log.status == HarvestLog.STATUS.succeeded
        assert log.raw_data.count() == (count if limit is None or count < limit else limit)

        if limit is not None and rediscovered:
            assert RawDatum.objects.filter().count() >= rediscovered
            assert RawDatum.objects.filter().count() <= rediscovered + max(0, min(limit, count - rediscovered))
        else:
            assert RawDatum.objects.filter().count() == (count if limit is None or count < limit else limit)

        if ingest:
            if superfluous:
                assert mock_ingest_task().apply_async.call_count == min(count, limit or 99999)
            elif limit is not None:
                assert mock_ingest_task().apply_async.call_count <= min(limit, count)
                assert mock_ingest_task().apply_async.call_count >= min(limit, count) - rediscovered
            else:
                assert mock_ingest_task().apply_async.call_count == count - rediscovered
        else:
            assert mock_ingest_task().apply_async.call_count == 0
