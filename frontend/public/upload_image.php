<?
/**
 * This file is part of Slideshow.
 * Copyright (C) 2008 David Sveningsson <ext@sidvind.com>
 * 
 * Slideshow is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Slideshow is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Slideshow.  If not, see <http://www.gnu.org/licenses/>.
 */
?>
<?

require_once("../settings.inc.php");
require_once("../db_functions.inc.php");

$name = $_FILES['filename']['name'];
$hash = crc32(uniqid());
$fullpath = "$image_dir/{$hash}_$name";

move_uploaded_file($_FILES['filename']['tmp_name'], $fullpath);

connect();
q("INSERT INTO files (fullpath) VALUES ('$fullpath')");
disconnect();

header('Location: index.php');

?>