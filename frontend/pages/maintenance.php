<?
/**
 * This file is part of Slideshow.
 * Copyright (C) 2008 David Sveningsson <ext@sidvind.com>
 *
 * Slideshow is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * Slideshow is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Slideshow.  If not, see <http://www.gnu.org/licenses/>.
 */
?>
<?

require_once('../core/module.inc.php');

class Maintenance extends Module {
	function __construct(){
		connect();
	}

	function __descturuct(){
		disconnect();
	}

	function index(){
		global $settings, $daemon;

		$arguments = $this->_get_arguments_from_settings();

		$ret =  array(
			'log' => array(),
			'activity' => array(),
			'status' => $daemon->get_status(),
			'cmd' => $daemon->generate_cmd($arguments, false),
			'cwd' => $arguments->basepath()
		);

		try {
			$activity_log = $settings->activity_log();
			$ret['activity'] = $activity_log->read_lines(25);
		} catch ( Exception $e ){}

		try {
			$log = $settings->log();

			$ret['log'] = $log->read_lines(25);
		} catch ( Exception $e ){}

		return $ret;
	}

	private function _get_arguments_from_settings(){
		global $settings;

		$arguments = new DaemonArguments;

		$arguments->set_database_settings($settings->database_hostname(), $settings->database_name(), $settings->database_username(), $settings->database_password());
		$arguments->set_resolution($settings->resolution_as_string());
		$arguments->set_logfile($settings->log_file());
		$arguments->set_bin_id($settings->current_bin());
		$arguments->set_basepath($settings->base_path());

		return $arguments;
	}

	function forcestart(){
		global $daemon;
  		$arguments = $this->_get_arguments_from_settings();
		$daemon->start($arguments, true);
		Module::redirect('/index.php/maintenance', array("show_debug"));
	}

	function start(){
		global $daemon;
		$arguments = $this->_get_arguments_from_settings();
		$daemon->start($arguments);
		Module::redirect('/index.php/maintenance', array("show_debug"));
	}

	function stop(){
		global $daemon;
		$daemon->stop();
		Module::redirect('/index.php/maintenance', array("show_debug"));
	}

	function coredump(){
		global $settings;

		$filename = $settings->base_path() . '/core';
		$filesize = filesize($filename);

		header("Pragma: public");
		header("Expires: 0");
		header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
		header("Cache-Control: private",false);
		header("Content-Transfer-Encoding: binary");
		header("Content-Type: application/octet-stream");
		header("Content-Length: " . $filesize);
		header("Content-Disposition: attachment; filename=\"core\";" );

		$file = fopen($filename, "rb");

		echo fread($file, $filesize);

		fclose($file);
	}

	function kill_mplayer(){
		`killall mplayer`;
		Module::redirect("index.php/maintenance");
	}

	function ping(){
		global $daemon;
		$daemon->ping();
		Module::redirect('/index.php/maintenance', array("show_debug"));
	}

	function debug_dumpqueue(){
		global $daemon;
		$daemon->debug_dumpqueue();
		Module::redirect('/index.php/maintenance', array("show_debug"));
	}
};

?>