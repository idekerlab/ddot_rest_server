#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddot_taskrunner` script."""

import os
import json
import unittest
import shutil
import tempfile
from unittest.mock import MagicMock


import ddot_rest_server
from ddot_rest_server import ddot_taskrunner as dt
from ddot_rest_server.ddot_taskrunner import FileBasedTask
from ddot_rest_server.ddot_taskrunner import FileBasedSubmittedTaskFactory
from ddot_rest_server.ddot_taskrunner import DeletedFileBasedTaskFactory
from ddot_rest_server.ddot_taskrunner import DDotTaskRunner


class TestDdotTaskRunner(unittest.TestCase):
    """Tests for `ddot_taskrunner` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_parse_arguments(self):
        """Test something."""
        res = dt._parse_arguments('hi', ['foo'])
        self.assertEqual(res.taskdir, 'foo')

        self.assertEqual(res.wait_time, 30)
        self.assertEqual(res.disabledelete, False)

    def test_filebasedtask_getter_setter_on_basic_obj(self):

        task = FileBasedTask(None, None)
        self.assertEqual(task.get_task_uuid(), None)
        self.assertEqual(task.get_ipaddress(), None)
        self.assertEqual(task.get_alpha(), None)
        self.assertEqual(task.get_beta(), None)
        self.assertEqual(task.get_state(), None)
        self.assertEqual(task.get_taskdict(), None)
        self.assertEqual(task.get_taskdir(), None)
        self.assertEqual(task.get_interactionfile(), None)

        self.assertEqual(task.get_task_summary_as_str(),
                         "{'basedir': None, 'state': None,"
                         " 'ipaddr': None, 'uuid': None}")

        task.set_result_data('result')

        task.set_taskdir('/foo')
        self.assertEqual(task.get_taskdir(), '/foo')

        task.set_taskdict({ddot_rest_server.ALPHA_PARAM: None})
        self.assertEqual(task.get_alpha(), None)

        task.set_taskdict({})
        self.assertEqual(task.get_alpha(), None)

        temp_dir = tempfile.mkdtemp()
        try:
            task.set_taskdir(temp_dir)
            thefile = os.path.join(temp_dir,
                                   ddot_rest_server.INTERACTION_FILE_PARAM)
            open(thefile, 'a').close()
            self.assertEqual(task.get_interactionfile(), thefile)
        finally:
            shutil.rmtree(temp_dir)

        task.set_taskdict({ddot_rest_server.ALPHA_PARAM: 0.1,
                           ddot_rest_server.BETA_PARAM: 1.2,
                           })
        self.assertEqual(task.get_alpha(), 0.1)
        self.assertEqual(task.get_beta(), 1.2)

    def test_filebasedtask_get_uuid_ip_state_basedir_from_path(self):
        # taskdir is none
        task = FileBasedTask(None, None)
        res = task._get_uuid_ip_state_basedir_from_path()
        self.assertEqual(res[FileBasedTask.BASEDIR], None)
        self.assertEqual(res[FileBasedTask.STATE], None)
        self.assertEqual(res[FileBasedTask.IPADDR], None)
        self.assertEqual(res[FileBasedTask.UUID], None)

        # too basic a path
        task.set_taskdir('/foo')
        res = task._get_uuid_ip_state_basedir_from_path()
        self.assertEqual(res[FileBasedTask.BASEDIR], '/')
        self.assertEqual(res[FileBasedTask.STATE], None)
        self.assertEqual(res[FileBasedTask.IPADDR], None)
        self.assertEqual(res[FileBasedTask.UUID], 'foo')

        # valid path
        task.set_taskdir('/b/submitted/i/myjob')
        res = task._get_uuid_ip_state_basedir_from_path()
        self.assertEqual(res[FileBasedTask.BASEDIR], '/b')
        self.assertEqual(res[FileBasedTask.STATE], 'submitted')
        self.assertEqual(res[FileBasedTask.IPADDR], 'i')
        self.assertEqual(res[FileBasedTask.UUID], 'myjob')

        # big path
        task.set_taskdir('/a/c/b/submitted/i/myjob')
        res = task._get_uuid_ip_state_basedir_from_path()
        self.assertEqual(res[FileBasedTask.BASEDIR], '/a/c/b')
        self.assertEqual(res[FileBasedTask.STATE], 'submitted')
        self.assertEqual(res[FileBasedTask.IPADDR], 'i')
        self.assertEqual(res[FileBasedTask.UUID], 'myjob')

    def test_save_task(self):
        temp_dir = tempfile.mkdtemp()
        try:
            task = FileBasedTask(None, None)
            self.assertEqual(task.save_task(), 'Task dir is None')

            # try with None for dictionary
            task.set_taskdir(temp_dir)
            self.assertEqual(task.save_task(), 'Task dict is None')

            # try with taskdir set to file
            task.set_taskdict('hi')
            somefile = os.path.join(temp_dir, 'somefile')
            open(somefile, 'a').close()
            task.set_taskdir(somefile)
            self.assertEqual(task.save_task(), somefile +
                             ' is not a directory')

            # try with string set as dictionary
            task.set_taskdict('hi')
            task.set_taskdir(temp_dir)
            self.assertEqual(task.save_task(), None)

            task.set_taskdict({'blah': 'value'})
            self.assertEqual(task.save_task(), None)
            tfile = os.path.join(temp_dir, ddot_rest_server.TASK_JSON)
            with open(tfile, 'r') as f:
                self.assertEqual(f.read(), '{"blah": "value"}')

            # test with result set
            task.set_result_data({'result': 'data'})
            self.assertEqual(task.save_task(), None)
            rfile = os.path.join(temp_dir, ddot_rest_server.RESULT)
            with open(rfile, 'r') as f:
                self.assertEqual(f.read(), '{"result": "data"}')
        finally:
            shutil.rmtree(temp_dir)

    def test_move_task(self):
        temp_dir = tempfile.mkdtemp()
        try:
            submitdir = os.path.join(temp_dir, ddot_rest_server.SUBMITTED_STATUS)
            os.makedirs(submitdir, mode=0o755)
            processdir = os.path.join(temp_dir, ddot_rest_server.PROCESSING_STATUS)
            os.makedirs(processdir, mode=0o755)
            donedir = os.path.join(temp_dir, ddot_rest_server.DONE_STATUS)
            os.makedirs(donedir, mode=0o755)

            # try a move on unset task
            task = FileBasedTask(None, None)
            self.assertEqual(task.move_task(ddot_rest_server.PROCESSING_STATUS),
                             'Unable to extract state basedir from task path')

            # try a move from submit to process
            ataskdir = os.path.join(submitdir, '192.168.1.1', 'qwerty-qwerty')
            os.makedirs(ataskdir)
            task = FileBasedTask(ataskdir, {'hi': 'bye'})

            self.assertEqual(task.save_task(), None)

            # try a move from submit to submit
            self.assertEqual(task.move_task(ddot_rest_server.SUBMITTED_STATUS),
                             None)
            self.assertEqual(task.get_taskdir(), ataskdir)

            # try a move from submit to process
            self.assertEqual(task.move_task(ddot_rest_server.PROCESSING_STATUS),
                             None)
            self.assertTrue(not os.path.isdir(ataskdir))
            self.assertTrue(os.path.isdir(task.get_taskdir()))
            self.assertTrue(ddot_rest_server.PROCESSING_STATUS in
                            task.get_taskdir())

            # try a move from process to done
            self.assertEqual(task.move_task(ddot_rest_server.DONE_STATUS),
                             None)
            self.assertTrue(ddot_rest_server.DONE_STATUS in
                            task.get_taskdir())

            # try a move from done to submitted
            self.assertEqual(task.move_task(ddot_rest_server.SUBMITTED_STATUS),
                             None)
            self.assertTrue(ddot_rest_server.SUBMITTED_STATUS in
                            task.get_taskdir())

            # try a move from submitted to error
            self.assertEqual(task.move_task(ddot_rest_server.ERROR_STATUS),
                             None)
            self.assertTrue(ddot_rest_server.DONE_STATUS in
                            task.get_taskdir())
            tjson = os.path.join(task.get_taskdir(), ddot_rest_server.TASK_JSON)
            with open(tjson, 'r') as f:
                data = json.load(f)
                self.assertEqual(data[ddot_rest_server.ERROR_PARAM],
                                 'Unknown error')

            # try a move from error to submitted then back to error again
            # with message this time
            self.assertEqual(task.move_task(ddot_rest_server.SUBMITTED_STATUS),
                             None)
            self.assertEqual(task.move_task(ddot_rest_server.ERROR_STATUS,
                                            error_message='bad'),
                             None)
            tjson = os.path.join(task.get_taskdir(), ddot_rest_server.TASK_JSON)
            with open(tjson, 'r') as f:
                data = json.load(f)
                self.assertEqual(data[ddot_rest_server.ERROR_PARAM],
                                 'bad')
        finally:
            shutil.rmtree(temp_dir)

    def test_filebasedtask_delete_temp_files(self):
        temp_dir = tempfile.mkdtemp()
        try:
            processdir = os.path.join(temp_dir, ddot_rest_server.PROCESSING_STATUS)
            os.makedirs(processdir, mode=0o755)
            donedir = os.path.join(temp_dir, ddot_rest_server.DONE_STATUS)
            os.makedirs(donedir, mode=0o755)
            ataskdir = os.path.join(processdir, '192.168.1.1', 'qwerty-qwerty')
            os.makedirs(ataskdir)
            taskdict = {'hi': 'bye'}
            task = FileBasedTask(ataskdir, taskdict)
            self.assertEqual(task.save_task(), None)

            # try move with delete true, but no file to delete
            self.assertEqual(task.move_task(ddot_rest_server.DONE_STATUS,
                                            delete_temp_files=True), None)

            # move task back to processing
            self.assertEqual(task.move_task(ddot_rest_server.PROCESSING_STATUS),
                             None)

            # add file and try move to done with delete set to false
            tmpfile = os.path.join(task.get_taskdir(),
                                   ddot_rest_server.TMP_RESULT)
            open(tmpfile, 'a').close()

            self.assertEqual(task.move_task(ddot_rest_server.DONE_STATUS),
                             None)

            self.assertTrue(os.path.isfile(task.get_tmp_resultpath()))

            # move back and try move to done with delete set to true
            self.assertEqual(task.move_task(ddot_rest_server.PROCESSING_STATUS),
                             None)

            self.assertEqual(task.move_task(ddot_rest_server.DONE_STATUS,
                                            delete_temp_files=True),
                             None)
        finally:
            shutil.rmtree(temp_dir)

    def test_filebasedtask_delete_task_files(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # try where taskdir is none
            task = FileBasedTask(None, None)
            self.assertEqual(task.delete_task_files(),
                             'Task directory is None')

            # try where taskdir is not a directory
            notadir = os.path.join(temp_dir, 'notadir')
            task = FileBasedTask(notadir, None)
            self.assertEqual(task.delete_task_files(),
                             'Task directory ' + notadir +
                             ' is not a directory')

            # try on empty directory
            emptydir = os.path.join(temp_dir, 'emptydir')
            os.makedirs(emptydir, mode=0o755)
            task = FileBasedTask(emptydir, None)
            self.assertEqual(task.delete_task_files(), None)
            self.assertFalse(os.path.isdir(emptydir))

            # try with result, snp, and task.json files
            valid_dir = os.path.join(temp_dir, 'yoyo')
            os.makedirs(valid_dir, mode=0o755)
            open(os.path.join(valid_dir, ddot_rest_server.RESULT), 'a').close()
            open(os.path.join(valid_dir, ddot_rest_server.TASK_JSON),
                 'a').close()
            open(os.path.join(valid_dir,
                              ddot_rest_server.INTERACTION_FILE_PARAM),
                 'a').close()

            task = FileBasedTask(valid_dir, {})
            self.assertEqual(task.delete_task_files(), None)
            self.assertFalse(os.path.isdir(valid_dir))

            # try where extra file causes os.rmdir to fail
            valid_dir = os.path.join(temp_dir, 'yoyo')
            os.makedirs(valid_dir, mode=0o755)
            open(os.path.join(valid_dir, 'somefile'), 'a').close()

            open(os.path.join(valid_dir, ddot_rest_server.RESULT), 'a').close()
            open(os.path.join(valid_dir, ddot_rest_server.TASK_JSON),
                 'a').close()
            open(os.path.join(valid_dir,
                              ddot_rest_server.INTERACTION_FILE_PARAM),
                 'a').close()
            task = FileBasedTask(valid_dir, {})
            self.assertTrue('trying to remove ' in task.delete_task_files())
            self.assertTrue(os.path.isdir(valid_dir))

        finally:
            shutil.rmtree(temp_dir)

    def test_filebasedsubmittedtaskfactory_get_next_task_taskdirnone(self):
        fac = FileBasedSubmittedTaskFactory(None)
        self.assertEqual(fac.get_next_task(), None)

    def test_filebasedsubmittedtaskfactory_get_next_task(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # no submit dir
            fac = FileBasedSubmittedTaskFactory(temp_dir)
            self.assertEqual(fac.get_next_task(), None)

            # empty submit dir
            sdir = os.path.join(temp_dir, ddot_rest_server.SUBMITTED_STATUS)
            os.makedirs(sdir, mode=0o755)
            self.assertEqual(fac.get_next_task(), None)

            # submit dir with file in it
            sdirfile = os.path.join(sdir, 'somefile')
            open(sdirfile, 'a').close()
            self.assertEqual(fac.get_next_task(), None)

            # submit dir with 1 subdir, but that is empty too
            ipsubdir = os.path.join(sdir, '1.2.3.4')
            os.makedirs(ipsubdir, mode=0o755)
            self.assertEqual(fac.get_next_task(), None)

            # submit dir with 1 subdir, with a file in it for some reason
            afile = os.path.join(ipsubdir, 'hithere')
            open(afile, 'a').close()
            self.assertEqual(fac.get_next_task(), None)

            # empty task dir
            taskdir = os.path.join(ipsubdir, 'sometask')
            os.makedirs(taskdir, mode=0o755)
            self.assertEqual(fac.get_next_task(), None)

            # empty json file
            taskjsonfile = os.path.join(taskdir, ddot_rest_server.TASK_JSON)
            open(taskjsonfile, 'a').close()
            self.assertEqual(fac.get_next_task(), None)
            self.assertEqual(fac.get_size_of_problem_list(), 1)
            plist = fac.get_problem_list()
            self.assertEqual(plist[0], taskdir)

            # try invalid json file

            # try with another task this time valid
            fac = FileBasedSubmittedTaskFactory(temp_dir)
            anothertask = os.path.join(sdir, '4.5.6.7', 'goodtask')
            os.makedirs(anothertask, mode=0o755)
            goodjson = os.path.join(anothertask, ddot_rest_server.TASK_JSON)
            with open(goodjson, 'w') as f:
                json.dump({'hi': 'there'}, f)

            res = fac.get_next_task()
            self.assertEqual(res.get_taskdict(), {'hi': 'there'})
            self.assertEqual(fac.get_size_of_problem_list(), 0)

            # try again since we didn't move it
            res = fac.get_next_task()
            self.assertEqual(res.get_taskdict(), {'hi': 'there'})
            self.assertEqual(fac.get_size_of_problem_list(), 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_nbgwastaskrunner_run_tasks_no_work(self):
        mocktaskfac = MagicMock()
        mocktaskfac.get_next_task = MagicMock(side_effect=[None, None])
        runner = DDotTaskRunner(wait_time=0, taskfactory=mocktaskfac)
        loop = MagicMock()
        loop.side_effect = [True, True, False]
        runner.run_tasks(keep_looping=loop)
        self.assertEqual(loop.call_count, 3)
        self.assertEqual(mocktaskfac.get_next_task.call_count, 2)

    def test_nbgwastaskrunner_run_tasks_task_raises_exception(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mocktaskfac = MagicMock()
            mocktask = MagicMock()
            mocktask.get_taskdir = MagicMock(return_value=temp_dir)
            mocktask.move_task = MagicMock()
            mocktaskfac.get_next_task.side_effect = [None, mocktask]

            mock_net_fac = MagicMock()
            mock_net_fac. \
                get_networkx_object = MagicMock(side_effect=Exception('foo'))

            runner = DDotTaskRunner(wait_time=0,
                                      taskfactory=mocktaskfac)
            loop = MagicMock()
            loop.side_effect = [True, True, False]
            runner.run_tasks(keep_looping=loop)
            self.assertEqual(loop.call_count, 3)
            self.assertEqual(mocktaskfac.get_next_task.call_count, 2)
        finally:
            shutil.rmtree(temp_dir)

    def test_nbgwastaskrunner_remove_deleted_task(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # try where delete task factory is none
            runner = DDotTaskRunner(wait_time=0)
            self.assertEqual(runner._remove_deleted_task(), False)

            # try where no task is returned
            mockfac = MagicMock()
            mockfac.get_next_task = MagicMock(return_value=None)
            runner = DDotTaskRunner(wait_time=0,
                                      deletetaskfactory=mockfac)
            res = runner._remove_deleted_task()
            self.assertEqual(res, False)
            mockfac.get_next_task.assert_called()

            # try where task.get_taskdir() is None
            task = MagicMock()
            task.get_taskdir = MagicMock(return_value=None)
            mockfac.get_next_task = MagicMock(return_value=task)
            runner = DDotTaskRunner(wait_time=0,
                                      deletetaskfactory=mockfac)
            res = runner._remove_deleted_task()
            self.assertEqual(res, True)
            mockfac.get_next_task.assert_called()
            task.get_taskdir.assert_called()

            # try where task.delete_task_files() raises Exception
            task = MagicMock()
            task.get_taskdir = MagicMock(return_value='/foo')
            task.delete_task_files = MagicMock(side_effect=Exception('some '
                                                                     'error'))
            mockfac.get_next_task = MagicMock(return_value=task)
            runner = DDotTaskRunner(wait_time=0,
                                      deletetaskfactory=mockfac)
            res = runner._remove_deleted_task()
            self.assertEqual(res, False)
            mockfac.get_next_task.assert_called()
            task.get_taskdir.assert_called()
            task.delete_task_files.assert_called()

            # try with valid task to delete, but delete returns message
            task = MagicMock()
            task.get_taskdir = MagicMock(return_value='/foo')
            task.delete_task_files = MagicMock(return_value='a error')
            mockfac.get_next_task = MagicMock(return_value=task)
            runner = DDotTaskRunner(wait_time=0,
                                      deletetaskfactory=mockfac)
            res = runner._remove_deleted_task()
            self.assertEqual(res, True)
            mockfac.get_next_task.assert_called()
            task.get_taskdir.assert_called()
            task.delete_task_files.assert_called()

            # try with valid task to delete
            task = MagicMock()
            task.get_taskdir = MagicMock(return_value='/foo')
            task.delete_task_files = MagicMock(return_value=None)
            mockfac.get_next_task = MagicMock(return_value=task)
            runner = DDotTaskRunner(wait_time=0,
                                      deletetaskfactory=mockfac)
            res = runner._remove_deleted_task()
            self.assertEqual(res, True)
            mockfac.get_next_task.assert_called()
            task.get_taskdir.assert_called()
            task.delete_task_files.assert_called()
        finally:
            shutil.rmtree(temp_dir)

    def test_deletefilebasedtaskfactory_get_task_with_id(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # try where taskdir is not set
            tfac = DeletedFileBasedTaskFactory(None)
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res, None)

            # try with valid taskdir
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res, None)

            # try where we match in submit dir, but match is not
            # a directory
            submitfile = os.path.join(temp_dir, ddot_rest_server.SUBMITTED_STATUS,
                                      '1.2.3.4', 'foo')
            os.makedirs(os.path.dirname(submitfile), mode=0o755)
            open(submitfile, 'a').close()
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res, None)
            os.unlink(submitfile)

            # try where we match in submit dir, but no json file
            submitdir = os.path.join(temp_dir, ddot_rest_server.SUBMITTED_STATUS,
                                     '1.2.3.4', 'foo')
            os.makedirs(submitdir, mode=0o755)
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res.get_taskdir(), submitdir)

            # try where we match in submit dir and there is a json file
            taskfile = os.path.join(submitdir,
                                    ddot_rest_server.TASK_JSON)
            with open(taskfile, 'w') as f:
                json.dump({ddot_rest_server.REMOTEIP_PARAM: '1.2.3.4'}, f)
                f.flush()

            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res.get_taskdir(), submitdir)
            self.assertEqual(res.get_ipaddress(), '1.2.3.4')

            # try where loading json file raises exception
            os.unlink(taskfile)
            open(taskfile, 'a').close()
            res = tfac._get_task_with_id('foo')
            self.assertEqual(res.get_taskdir(), submitdir)
            self.assertEqual(res.get_taskdict(), {})
            shutil.rmtree(submitdir)

            # try where we match in processing dir
            procdir = os.path.join(temp_dir, ddot_rest_server.PROCESSING_STATUS,
                                   '4.5.5.5',
                                   '02e487ef-79df-4d99-8f22-1ff1d6d52a2a')
            os.makedirs(procdir, mode=0o755)
            res = tfac._get_task_with_id('02e487ef-79df-4d99-8f22-'
                                         '1ff1d6d52a2a')
            self.assertEqual(res.get_taskdir(), procdir)
            shutil.rmtree(procdir)

            # try where we match in done dir
            donedir = os.path.join(temp_dir, ddot_rest_server.DONE_STATUS,
                                   '192.168.5.5',
                                   '02e487ef-79df-4d99-8f22-1ff1d6d52a2a')
            os.makedirs(donedir, mode=0o755)
            res = tfac._get_task_with_id('02e487ef-79df-4d99-8f22-'
                                         '1ff1d6d52a2a')
            self.assertEqual(res.get_taskdir(), donedir)

        finally:
            shutil.rmtree(temp_dir)

    def test_deletefilebasedtaskfactory_get_next_task(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # test where delete request dir is None
            tfac = DeletedFileBasedTaskFactory(None)
            res = tfac.get_next_task()
            self.assertEqual(res, None)

            # test where delete request dir is not a directory
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac.get_next_task()
            self.assertEqual(res, None)

            # no delete requests found
            del_req_dir = os.path.join(temp_dir, ddot_rest_server.DELETE_REQUESTS)
            os.makedirs(del_req_dir, mode=0o755)
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac.get_next_task()
            self.assertEqual(res, None)

            # directory in delete requests dir
            dir_in_del_dir = os.path.join(del_req_dir, 'uhohadir')
            os.makedirs(dir_in_del_dir, mode=0o755)
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac.get_next_task()
            self.assertEqual(res, None)

            # Found a delete request, but no task found in system
            a_request = os.path.join(del_req_dir,
                                     '02e487ef-79df-4d99-8f22-1ff1d6d52a2a')
            with open(a_request, 'w') as f:
                f.write('1.2.3.4')
                f.flush()
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac.get_next_task()
            self.assertEqual(res, None)
            self.assertTrue(not os.path.isfile(a_request))

            # Found a valid request in system
            a_request = os.path.join(del_req_dir,
                                     '02e487ef-79df-4d99-8f22-1ff1d6d52a2a')
            with open(a_request, 'w') as f:
                f.write('1.2.3.4')
                f.flush()
            done_dir = os.path.join(temp_dir, ddot_rest_server.DONE_STATUS,
                                    '1.2.3.4',
                                    '02e487ef-79df-4d99-8f22-1ff1d6d52a2a')
            os.makedirs(done_dir, mode=0o755)
            tfac = DeletedFileBasedTaskFactory(temp_dir)
            res = tfac.get_next_task()
            self.assertEqual(res.get_taskdir(), done_dir)
            self.assertEqual(res.get_taskdict(), {})
            self.assertTrue(not os.path.isfile(a_request))

        finally:
            shutil.rmtree(temp_dir)

    def test_main(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # test no work and disable delete true
            loop = MagicMock()
            loop.side_effect = [True, True, False]
            dt.main(['foo.py', '--wait_time', '0',
                     '--nodaemon',
                     temp_dir],
                    keep_looping=loop)

            # test no work and disable delete false
            loop = MagicMock()
            loop.side_effect = [True, True, False]
            dt.main(['foo.py', '--wait_time', '0',
                     '--nodaemon',
                     '--disabledelete',
                     temp_dir],
                    keep_looping=loop)

            # test exception catch works
            loop = MagicMock()
            loop.side_effect = Exception('some error')
            dt.main(['foo.py', '--wait_time', '0',
                     '--nodaemon',
                     temp_dir],
                    keep_looping=loop)
        finally:
            shutil.rmtree(temp_dir)
