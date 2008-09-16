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

#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <stdexcept>
#include "ErrorCodes.h"

/**
 * @brief Base exception.
 * You should never throw this specifically but rather catch it
 * when you wish to catch all exceptions.
 *
 * @param message The error message.
 */
class BaseException: public std::runtime_error {
	public:
		BaseException(const char* message): std::runtime_error(message){}
};

/**
 * @brief Fatal exceptions will cause the application to terminate.
 * The application will terminate but will try to cleanup.
 *
 * @param message The error message.
 * @param code The error code which will be returned.
 */
class FatalException: public BaseException {
	public:
		FatalException(const char* message, ErrorCode code): BaseException(message), _code(code){}
		ErrorCode code(){ return _code; }

	private:
		ErrorCode _code;
};

/**
 * @brief Causes the application to exit.
 * Throw this exception if you want to exit the application but want
 * it to shut down properly.
 */
class ExitException: public FatalException {
	public:
		ExitException(): FatalException(NULL, NO_ERROR){}
};

/**
 * @brief Xlib error.
 */
class XlibException: public FatalException {
	public:
		XlibException(const char* message): FatalException(message, XLIB_ERROR){}
};

#endif // EXCEPTIONS_H
