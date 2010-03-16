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

#include "module.h"
#include "Transition.h"
#include <GL/gl.h>
#include <math.h>

#ifndef M_PI
#	define M_PI           3.14159265358979323846 /* pi */
#endif

MODULE_INFO("Spin", TRANSITION_MODULE, "David Sveningsson");

int module_init(){
	return 0;
}

int module_cleanup(){
	return 0;
}

void render(transition_context_t* context){
	glClear(GL_COLOR_BUFFER_BIT);

	glPushMatrix();

	glRotatef( 20 * sinf(M_PI * context->state), 1, 0, 0);
	glTranslatef(0.5f, 0, 0);
	glRotatef( 180 * context->state, 0, 1, 0);

	glColor4f(1,1,1,1);

	glBindTexture(GL_TEXTURE_2D, context->texture[0]);
	glBegin( GL_QUADS );
		glTexCoord2f(1.0f, 0.0f); glVertex2f(-0.5f, 0.0f);
		glTexCoord2f(0.0f, 0.0f); glVertex2f( 0.5f, 0.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex2f( 0.5f, 1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex2f(-0.5f, 1.0f);
	glEnd();

	glBindTexture(GL_TEXTURE_2D, context->texture[1]);
	glBegin( GL_QUADS );
		glTexCoord2f(0.0f, 0.0f); glVertex2f(-0.5f, 0.0f);
		glTexCoord2f(0.0f, 1.0f); glVertex2f(-0.5f, 1.0f);
		glTexCoord2f(1.0f, 1.0f); glVertex2f( 0.5f, 1.0f);
		glTexCoord2f(1.0f, 0.0f); glVertex2f( 0.5f, 0.0f);
	glEnd();

	glPopMatrix();
}
