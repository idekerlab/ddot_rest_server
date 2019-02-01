#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddot_rest_server` package."""

import os
import json
import unittest
import shutil
import tempfile

import ddot_rest_server


class TestNbgwas_rest(unittest.TestCase):
    """Tests for `ddot_rest_server` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self._temp_dir = tempfile.mkdtemp()
        ddot_rest_server.app.testing = True
        ddot_rest_server.app.config[ddot_rest_server.JOB_PATH_KEY] = self._temp_dir
        ddot_rest_server.app.config[ddot_rest_server.WAIT_COUNT_KEY] = 1
        ddot_rest_server.app.config[ddot_rest_server.SLEEP_TIME_KEY] = 0
        self._app = ddot_rest_server.app.test_client()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self._temp_dir)

    def test_baseurl(self):
        """Test something."""
        rv = self._app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Fake Cytoscape Search' in str(rv.data))

    def test_delete(self):
        rv = self._app.delete(ddot_rest_server.DDOT_NS + '/yoyo')

        self.assertTrue(rv.status_code in [200, 410, 500])

        # try with not set path
        rv = self._app.delete(ddot_rest_server.DDOT_NS + '/')
        self.assertEqual(rv.status_code, 404)

    def test_get_status(self):
        rv = self._app.get(ddot_rest_server.DDOT_NS + '/status')
        data = json.loads(rv.data)
        self.assertTrue('status' in data or 'message' in data)
        self.assertTrue(rv.status_code in [200, 500])
