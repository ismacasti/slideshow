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

require_once('json.php');

class Node {
	public $tag;
	public $prev;

	public function __construct($tag, $prev){
		$this->tag = $tag;
		$this->prev = $prev;
	}
}

class Item {
	public $name;
	public $type;
	public $value;
	public $description;
	public $install;

	public function __construct($name, $type, $description, $install){
		$this->name = $name;
		$this->type = $type;
		$this->description = $description;
		$this->install = $install;
	}
}

class Group {
	public $name;
	public $description = NULL;
	public $items = array();

	public function __construct($name){
		$this->name = $name;
	}

	public function add_item($item){
		$this->items[$item->name] = $item;
	}
}

class XMLSettings {
	private $group;
	private $node = NULL;
	private $active_group = NULL;
	private $active_item = NULL;

	public function __construct($xmlfile){
		libxml_use_internal_errors(true);

		$doc = new DOMDocument;
		$doc->Load($xmlfile);

		if (!$doc->validate()) {
			echo "$xmlfile is not a valid XMLSettings file!\n";
		    $errors = libxml_get_errors();
		    foreach ($errors as $error) {
		    	echo basename($error->file), ':', $error->line, ' ', $error->message;
		    }

		    libxml_clear_errors();
		    die("");
		}

		$xml_parser = xml_parser_create();

		xml_set_element_handler($xml_parser, array($this, 'startElement'), array($this, 'endElement'));
		xml_set_character_data_handler($xml_parser, array($this, 'characterData'));

		$fp = fopen($xmlfile,'r');

		while ($data = fread($fp, 4096)){
		   xml_parse($xml_parser, $data, feof($fp));
		}

		fclose($fp);

		xml_parser_free($xml_parser);
	}

	public function merge_settings($filename){
		$data = json_decode(file_get_contents($filename), true );

		foreach ($data as $name => $group){
			if ( !array_key_exists($name, $this->group) ){
				continue;
			}

			foreach ($group as $itemname => $item){
				if ( !array_key_exists($itemname, $this->group[$name]->items) ){
					continue;
				}

				$this->group[$name]->items[$itemname]->value = $item;
			}
		}
	}

	public function add_group($group){
		$this->group[$group->name] = $group;
	}

	public function as_settings_json(){
		$data = array();

		foreach ( $this->group as $g ){
			$section = array();
			foreach ( $g->items as $item ){
				$section[$item->name] = $item->value != NULL ? $item->value : "";
			}
			$data[$g->name] = $section;
		}

		return pretty_json( json_encode($data) );
	}

	public function as_array($item_filter = NULL){
		$array = array();
		foreach ( $this->group as $name => $group ){
			$copy = new Group($name);
			$copy->description = $group->description;
			foreach ( $group->items as $itemname => $item ){
				if ( $item_filter && !call_user_func($item_filter, $item) ){
					continue;
				}
				$copy->add_item($item);
			}
			if ( count($copy) > 0 ){
				$array[$name] = $copy;
			}
		}

		return $array;
	}

	public function groups(){
		return $this->group;
	}

	public function startElement($parser, $name, $attrs) {
		$this->node = new Node($name, $this->node);

		switch ( $name ){
			case 'GROUP':
				$this->active_group = new Group($attrs['NAME']);
				$this->add_group($this->active_group);
				break;
			case 'ITEM':
				$description = NULL;
				if ( isset($attrs['DESCRIPTION']) ){
					$description = $attrs['DESCRIPTION'];
				}
				$install = false;
				if ( isset($attrs['INSTALL']) && $attrs['INSTALL'] == 'yes' ){
					$install = true;
				}
				$this->active_item = new Item($attrs['NAME'], $attrs['TYPE'], $description, $install);
				break;
		}
	}

	public function endElement($parser, $name) {
		$this->node = $this->node->prev;

		switch ( $name ){
			case 'ITEM':
				$this->active_group->add_item($this->active_item);
				break;
		}
	}

	public function characterData($parser, $data) {
		switch ( $this->node->tag ){
			case 'DESCRIPTION':
				$this->active_group->description = $data;
				break;
			case 'ITEM':
				switch ( $this->active_item->type ){
					case 'int':
						$this->active_item->value = (int)$data;
						break;
					case 'float':
						$this->active_item->value = (float)$data;
						break;
					case 'resolution':
						$this->active_item->value = sscanf($data, "%dx%d");
						break;
					default:
						$this->active_item->value = $data;
				}
		}
	}
}

?>