#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fake_cytoscapesearch` package."""


import os
import json
import unittest
import shutil
import tempfile
import re
import io
import uuid

from werkzeug.datastructures import FileStorage

import fake_cytoscapesearch


class TestNbgwas_rest(unittest.TestCase):
    """Tests for `fake_cytoscapesearch` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self._temp_dir = tempfile.mkdtemp()
        fake_cytoscapesearch.app.testing = True
        fake_cytoscapesearch.app.config[fake_cytoscapesearch.JOB_PATH_KEY] = self._temp_dir
        fake_cytoscapesearch.app.config[fake_cytoscapesearch.WAIT_COUNT_KEY] = 1
        fake_cytoscapesearch.app.config[fake_cytoscapesearch.SLEEP_TIME_KEY] = 0
        self._app = fake_cytoscapesearch.app.test_client()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self._temp_dir)

    def test_baseurl(self):
        """Test something."""
        rv = self._app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Fake Cytoscape Search' in str(rv.data))

    def test_delete(self):
        rv = self._app.delete(fake_cytoscapesearch.CYTOSEARCH_NS + '/yoyo')

        self.assertTrue(rv.status_code in [200, 410, 500])

        # try with not set path
        rv = self._app.delete(fake_cytoscapesearch.CYTOSEARCH_NS + '/')
        self.assertEqual(rv.status_code, 405)

    def test_get_status(self):
        rv = self._app.get(fake_cytoscapesearch.CYTOSEARCH_NS + '/status')
        data = json.loads(rv.data)
        self.assertTrue('status' in data or 'message' in data)
        self.assertTrue(rv.status_code in [200, 500])
