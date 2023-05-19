package term


const (
	ASCII_SEQ				= "\x1B["
)

// Color
const (
	BACKGROUND_COLOR		= "48;"
	FORGROUND_COLOR			= "38;"

	COLOR_BLACK				= "30m"
	COLOR_RED				= "31m"
	COLOR_GREEN				= "32m"
	COLOR_YELLOW			= "33m"
	COLOR_BLUE				= "34m"
	COLOR_MAGENTA			= "35m"
	COLOR_CYAN				= "36m"
	COLOR_WHITE				= "37m"
)

// Cursor control
const (
	CURSOR_SCROLL_MOVE_UP		= "nA"
	CURSOR_SCROLL_MOVE_DOWN 	= "nB"
	CURSOR_SCROLL_MOVE_RIGHT 	= "nC"
	CURSOR_SCROLL_MOVE_LEFT 	= "nD"

	CURSOR_SHOW					= "?25h"
	CURSOR_HIDE					= "?25l"

)

const (

)