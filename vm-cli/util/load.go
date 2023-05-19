package util

import (
	"strconv"

	// "fmt"
	"os"
)

var Spinners = map[int][]string{
	0:  {"←", "↖", "↑", "↗", "→", "↘", "↓", "↙"},
	1:  {"▁", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▁"},
	2:  {"▖", "▘", "▝", "▗"},
	3:  {"┤", "┘", "┴", "└", "├", "┌", "┬", "┐"},
	4:  {"◢", "◣", "◤", "◥"},
	5:  {"◰", "◳", "◲", "◱"},
	6:  {"◴", "◷", "◶", "◵"},
	7:  {"◐", "◓", "◑", "◒"},
	8:  {".", "o", "O", "@", "*"},
	9:  {"|", "/", "-", "\\"},
	10: {"◡◡", "⊙⊙", "◠◠"},
	11: {"⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽", "⣾"},
	12: {"⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"},
	13: {"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"},
	14: {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"},
	15: {"▉", "▊", "▋", "▌", "▍", "▎", "▏", "▎", "▍", "▌", "▋", "▊", "▉"},
	16: {"■", "□", "▪", "▫"},
	17: {"←", "↑", "→", "↓"},
	18: {"╫", "╪"},
	19: {"⇐", "⇖", "⇑", "⇗", "⇒", "⇘", "⇓", "⇙"},
	20: {"⠁", "⠁", "⠉", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠤", "⠄", "⠄", "⠤", "⠠", "⠠", "⠤", "⠦", "⠖", "⠒", "⠐", "⠐", "⠒", "⠓", "⠋", "⠉", "⠈", "⠈"},
	21: {"⠈", "⠉", "⠋", "⠓", "⠒", "⠐", "⠐", "⠒", "⠖", "⠦", "⠤", "⠠", "⠠", "⠤", "⠦", "⠖", "⠒", "⠐", "⠐", "⠒", "⠓", "⠋", "⠉", "⠈"},
	22: {"⠁", "⠉", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠤", "⠄", "⠄", "⠤", "⠴", "⠲", "⠒", "⠂", "⠂", "⠒", "⠚", "⠙", "⠉", "⠁"},
	23: {"⠋", "⠙", "⠚", "⠒", "⠂", "⠂", "⠒", "⠲", "⠴", "⠦", "⠖", "⠒", "⠐", "⠐", "⠒", "⠓", "⠋"},
	24: {"ｦ", "ｧ", "ｨ", "ｩ", "ｪ", "ｫ", "ｬ", "ｭ", "ｮ", "ｯ", "ｱ", "ｲ", "ｳ", "ｴ", "ｵ", "ｶ", "ｷ", "ｸ", "ｹ", "ｺ", "ｻ", "ｼ", "ｽ", "ｾ", "ｿ", "ﾀ", "ﾁ", "ﾂ", "ﾃ", "ﾄ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ", "ﾊ", "ﾋ", "ﾌ", "ﾍ", "ﾎ", "ﾏ", "ﾐ", "ﾑ", "ﾒ", "ﾓ", "ﾔ", "ﾕ", "ﾖ", "ﾗ", "ﾘ", "ﾙ", "ﾚ", "ﾛ", "ﾜ", "ﾝ"},
	25: {".", "..", "..."},
	26: {"▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▉", "▊", "▋", "▌", "▍", "▎", "▏", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"},
	27: {".", "o", "O", "°", "O", "o", "."},
	28: {"+", "x"},
	29: {"v", "<", "^", ">"},
	30: {"🌍", "🌎", "🌏"},
	31: {"◜", "◝", "◞", "◟"},
	32: {"⬒", "⬔", "⬓", "⬕"},
	33: {"⬖", "⬘", "⬗", "⬙"},
	34: {"♠", "♣", "♥", "♦"},
	35: {"➞", "➟", "➠", "➡", "➠", "➟"},
	36: {"⎺", "⎻", "⎼", "⎽", "⎼", "⎻"},
	37: {"✶", "✸", "✹", "✺", "✹", "✷"},
	38: {"¿", "?"},
	39: {"⢹", "⢺", "⢼", "⣸", "⣇", "⡧", "⡗", "⡏"},
	40: {"⢄", "⢂", "⢁", "⡁", "⡈", "⡐", "⡠"},
	41: {".", "o", "O", "°", "O", "o", "."},
	42: {"▓", "▒", "░"},
	43: {"▌", "▀", "▐", "▄"},
	44: {"⊶", "⊷"},
	45: {"▪", "▫"},
	46: {"□", "■"},
	47: {"▮", "▯"},
	48: {"-", "=", "≡"},
	49: {"d", "q", "p", "b"},
	50: {"🌑 ", "🌒 ", "🌓 ", "🌔 ", "🌕 ", "🌖 ", "🌗 ", "🌘 "},
	51: {"☗", "☖"},
	52: {"⧇", "⧆"},
	53: {"◉", "◎"},
	54: {"㊂", "㊀", "㊁"},
	55: {"⦾", "⦿"},
}

var Done = map[int]string{
	0: "✔",
}

var Error = map[int]string{
	0: "✖",
}

var Info = map[int]string{
	0: "!",
}

const RESET_LINE = "\r"
const RESET = "\033[0K"
const COLOR_RESET = "\033[38;2;255;255;255m"

type LoadSpinners struct {
	OptionSpinners int;
	OptionDone int;
	OptionInfo int;
	OptionError int;
	Index int;
	MaxIndex int;
	Message string;

	ColorSpin string;
	ColorDone string;
	ColorInfo string;
	ColorError string;

	Line int;
	Column int;
}

func NewSpinners(spinner int, done int, line int, column int) LoadSpinners {

	max := len(Spinners[spinner])


	return LoadSpinners{
		OptionSpinners: spinner,
		OptionDone: done,
		OptionInfo: 0,
		OptionError: 0,
		Index: 0,
		MaxIndex: max,
		Message: "Empty",
		
		ColorSpin: "\033[38;2;255;255;0m",
		ColorDone: "\033[38;2;0;255;0m",
		ColorInfo: "\033[38;2;255;0;255m",
		ColorError: "\033[38;2;255;0;0m",

		Line: line,
		Column: column,
	}
}

func (l *LoadSpinners) EditMessage(message string) {
	l.Message = message
}


func (l *LoadSpinners) Next() {


	message := RESET_LINE + Spinners[l.OptionSpinners][l.Index] + " : " + l.Message + RESET

	if l.Line != -1 && l.Column != -1 {

		message = RESET_LINE + "\033["+ strconv.Itoa(l.Line) +";"+strconv.Itoa(l.Column)+"H" + l.ColorSpin + Spinners[l.OptionSpinners][l.Index] + COLOR_RESET + " : " + l.Message + RESET

	}


	os.Stdout.Write([]byte(message))

	l.Index += 1

	if l.Index == l.MaxIndex {
		l.Index = 0
	}

}

func (l *LoadSpinners) Done(info bool, error bool) {

	
	message := RESET_LINE + Done[l.OptionDone] + " : " + l.Message

	if error {
		message = RESET_LINE + RESET_LINE + Error[l.OptionError] + " : " + l.Message
	}

	if l.Line != -1 && l.Column != -1 {

		message = RESET_LINE + "\033["+ strconv.Itoa(l.Line) +";"+strconv.Itoa(l.Column)+"H" + l.ColorDone + Done[l.OptionDone] + COLOR_RESET + " : " + l.Message

		if info {
			message = RESET_LINE + "\033["+ strconv.Itoa(l.Line) +";"+strconv.Itoa(l.Column)+"H" + l.ColorInfo + Info[l.OptionInfo] + COLOR_RESET + " : " + l.Message
		}

		if error {
			message = RESET_LINE + "\033["+ strconv.Itoa(l.Line) +";"+strconv.Itoa(l.Column)+"H" + l.ColorError + Error[l.OptionError] + COLOR_RESET + " : " + l.Message
		}

	}

	os.Stdout.Write([]byte(message))

}