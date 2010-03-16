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

#ifndef SLIDESHOW_MODULE_H
#define SLIDESHOW_MODULE_H

enum module_type_t {
	TRANSITION_MODULE,
	ASSEMBLER_MODULE
};

#define MODULE_INFO(name, type, author) \
	const char * __module_name = name; \
	const enum module_type_t __module_type = type; \
	const char * __module_author = author

#ifdef WIN32
#	ifdef BUILD_DLL
#		define EXPORT __declspec(dllexport)
#	else /* BUILD_DLL */
#		define EXPORT __declspec(dllimport)
#	endif /* BUILD_DLL */
#else /* WIN32 */
#	define EXPORt
#endif

#endif // SLIDESHOW_MODULE_H
