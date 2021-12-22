import os
import shutil
import zipfile
from pathlib import Path
from django.core.files.base import ContentFile

from django.test import TestCase
from django.test.client import Client
import pandas as pd

from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from apps.index import models

from modules import utils

STANDARD_TEST_LOG = Path("./cache/running-example.jsonocel")


def get_event_log():

    if not os.path.exists(STANDARD_TEST_LOG.parent):
        os.mkdir(STANDARD_TEST_LOG.parent)
    if not os.path.exists(STANDARD_TEST_LOG):
        os.system(
            "curl ocel-standard.org/1.0/running-example.jsonocel.zip >> "
            + str(STANDARD_TEST_LOG)
            + ".zip"
        )
        with zipfile.ZipFile(str(STANDARD_TEST_LOG) + ".zip", "r") as zip_ref:
            zip_ref.extractall(STANDARD_TEST_LOG.parent)

    tuple = ocel_importer.apply(str(STANDARD_TEST_LOG))
    #! This is not clean python, Do pull request for pm4pymdl project
    if len(tuple) == 2:
        df, obj_df = tuple
    else:
        df = tuple
        obj_df = pd.DataFrame()
    return df, obj_df


class AbstractTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.df, cls.obj_df = get_event_log()

    def setUp(self):
        self.df, self.obj_df = self.__class__.df, self.__class__.obj_df

    @classmethod
    def save_event_log_to_db(cls):
        json_string = utils.apply_json(cls.df, cls.obj_df)
        hash, log = utils.event_log_by_hash(json_string)
        event_log = models.EventLog.objects.create()
        event_log.name = os.path.splitext(STANDARD_TEST_LOG.name)[0]
        event_log.file.save(
            event_log.name + ".jsonocel",
            ContentFile(json_string),
        )
        event_log.hash = hash
        event_log.save()
        cls.event_log = event_log
        return event_log


class ModelTestCase(AbstractTestCase):
    def test_no_duplicate_logs(self):
        event_log = self.save_event_log_to_db()
        hash_2, log_2 = utils.event_log_by_hash(
            utils.apply_json(self.df, self.obj_df)
        )

        self.assertEqual(event_log.hash, hash_2)
        self.assertEqual(event_log.id, log_2.id)


class WebpageAvailabilityTestCase(AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.save_event_log_to_db()

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.event_log = self.__class__.event_log

    def test_upload_no_log(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "index/upload.html", [template.name for template in response.templates]
        )

    def test_upload_valid_log(self):
        response = self.client.get(f"?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "index/upload.html", [template.name for template in response.templates]
        )

    def test_upload_invalid_log(self):
        response = self.client.get(f"?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_filtering_no_log(self):
        response = self.client.get("/filtering")
        self.assertEqual(response.status_code, 404)

    def test_filtering_valid_log(self):
        response = self.client.get(f"/filtering?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "index/filtering.html", [template.name for template in response.templates]
        )
        self.assertContains(response, self.event_log.name)
        self.assertContains(response, 'id="btn-submit"')
        self.assertContains(response, 'name="id"')

    def test_filtering_invalid_log(self):
        response = self.client.get(f"/filtering?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_filter_no_log(self):
        response = self.client.get("/filter")
        self.assertEqual(response.status_code, 404)

    def test_filter_valid_log(self):
        response = self.client.get(f"/filter?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "index/filter.html", [template.name for template in response.templates]
        )
        self.assertContains(response, 'id="row-select"')
        self.assertContains(response, 'id="column-select"')
        self.assertContains(response, 'id="btn-create-cell"')
        self.assertContains(response, 'name="id"')

    def test_filter_invalid_log(self):
        response = self.client.get(f"/filter?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_visualization_no_log(self):
        response = self.client.get("/visualize")
        self.assertEqual(response.status_code, 404)

    def test_visualization_valid_log(self):
        response = self.client.get(f"/visualize?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "vis/vis.html", [template.name for template in response.templates]
        )
        self.assertContains(response, 'id="btn-dfg-freq"')
        self.assertContains(response, 'id="btn-dfg-perf"')
        self.assertContains(response, 'id="btn-petri"')
        self.assertContains(response, 'name="id"')

    def test_visualization_invalid_log(self):
        response = self.client.get(f"/visualize?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_comparative_no_log(self):
        response = self.client.get("/comparative")
        self.assertEqual(response.status_code, 404)

    def test_comparative_valid_log(self):
        response = self.client.get(f"/comparative?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "index/comparative.html", [template.name for template in response.templates]
        )

    def test_comparative_invalid_log(self):
        response = self.client.get(f"/comparative?id=foo")
        self.assertEqual(response.status_code, 404)


class PlotsTestCase(AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.save_event_log_to_db()

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.event_log = self.__class__.event_log
        self.longMessage = True

    def test_histogram_invalid_id(self):
        response = self.client.get(f"/plots/histogram/{self.df.columns[0]}?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_histogram_invalid_column(self):
        response = self.client.get(f"/plots/histogram/foo?id={self.event_log.id}")
        self.assertEqual(response.status_code, 404)

    def test_histogram_valid_event_columns(self):
        a, b, c = utils.get_column_types(self.df)
        for column in [*a, *b, *c]:
            response = self.client.get(
                f"/plots/histogram/{column}?id={self.event_log.id}"
            )
            self.assertEqual(response.status_code, 200, msg=f"Failed for {column}")
            # self.assertContains(response,"<div class=\"plot-container plotly\">")

    def test_histogram_valid_object_columns(self):
        obj_numerical, obj_categorical, _ = utils.get_column_types(self.obj_df)
        for column in [*obj_numerical, *obj_categorical]:
            response = self.client.get(
                f"/plots/histogram/{column}?id={self.event_log.id}"
            )
            self.assertEqual(response.status_code, 200)
            # self.assertContains(response,"<div class=\"plot-container plotly\">")

    def test_dfg_invalid_id(self):
        response = self.client.get(f"/plots/dfg?id=foo")
        self.assertEqual(response.status_code, 404)

    def test_dfg_valid(self):
        response = self.client.get(f"/plots/dfg?id={self.event_log.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")
