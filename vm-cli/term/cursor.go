package term

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"

	"golang.org/x/sys/unix"
)

type Cursor struct {
	Line int;
	Column int;
}

type TermSize struct {
	Line uint16;
	Column uint16;
	X uint16;
	Y uint16;
}

var s strings.Builder

func GetCursorPos() Cursor {

	setRawMode(true)

	seq := "\x1b[6n"
	os.Stdout.Write([]byte(seq))

	// Read in the result
	var buf bytes.Buffer
	reader := bufio.NewReader(os.Stdin)
	for {
		char, _, err := reader.ReadRune()
		if err != nil {
			break
		}
		if char == 'R' {
			break
		}
		buf.WriteRune(char)
	}

	// Set the terminal back from raw mode to 'cooked'
	setRawMode(false)

	result := buf.String()

	// Check for the desired output
	if strings.Contains(result, ";") {
		re := regexp.MustCompile(`\[(\d*);(\d*)`)
		matches := re.FindStringSubmatch(result)

		// fmt.Printf("%v", matches)

		line, _ := strconv.Atoi(matches[1])
		column, _ := strconv.Atoi(matches[2])

		return Cursor{
			Line: line,
			Column: column,
		}
	}

	return Cursor{
		Line: 0,
		Column: 0,
	}
}

func GetTermSize() (TermSize, error) {
	fd := unix.Stdout
	var ts TermSize
	uws, err := unix.IoctlGetWinsize(int(fd), unix.TIOCGWINSZ)
	if err != nil {
		return ts, err
	}

	ts.Line = uws.Row
	ts.Column = uws.Col
	ts.X = uws.Xpixel
	ts.Y = uws.Ypixel

	return ts, nil
}

func ScrollDown(line int) {
	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString(strconv.Itoa(line))
	s.WriteString("T")
	os.Stdout.Write([]byte(s.String()))
}

func ScrollUp(line int) {
	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString(strconv.Itoa(line))
	s.WriteString("S")
	os.Stdout.Write([]byte(s.String()))
}


func MoveDownCursor(line int) {

	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString(strconv.Itoa(line))
	s.WriteString("B")
	os.Stdout.Write([]byte(s.String()))
}

func MoveUpCursor(line int) {

	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString(strconv.Itoa(line))
	s.WriteString("A")
	os.Stdout.Write([]byte(s.String()))
}

func MoveCursor(line int, column int) {
	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString(strconv.Itoa(line))
	s.WriteString(";")
	s.WriteString(strconv.Itoa(column))
	s.WriteString("H\r")

	os.Stdout.Write([]byte(s.String()))
}

func HideCursor() {

	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString("?25l\r")

	os.Stdout.Write([]byte(s.String()))
}

func ShowCursor() {

	s.Reset()
	s.WriteString(ASCII_SEQ)
	s.WriteString("?25h\r")

	os.Stdout.Write([]byte(s.String()))
}







func setRawMode(enable bool) error {
	// Get the current terminal settings
	// var termios unix.Termios
	termios, err := unix.IoctlGetTermios(int(os.Stdin.Fd()), unix.TCGETS)
	if err != nil {
		return fmt.Errorf("error getting terminal attributes: %w", err)
	}

	// Save the original terminal settings
	origTermios := termios

	// Enable or disable raw mode as specified
	if enable {
		termios.Lflag &^= unix.ECHO | unix.ICANON | unix.ISIG
	} else {
		termios.Lflag |= unix.ECHO | unix.ICANON | unix.ISIG
	}

	// Set the modified terminal settings
	err = unix.IoctlSetTermios(int(os.Stdin.Fd()), unix.TCSETS, termios)
	if err != nil {
		return fmt.Errorf("error setting terminal attributes: %w", err)
	}

	// Restore the original terminal settings with a defer statement
	defer func() {
		unix.IoctlSetTermios(int(os.Stdin.Fd()), unix.TCSETS, origTermios)
	}()

	return nil
}
