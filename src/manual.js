const button_names = [
    "resetkey", "cursorupkey", "cursordownkey", "pageupkey", "pagedownkey", "alterkey", "insertkey",
    "deletekey", "eobkey", "cankey", "inputkey", "outputkey", "poskey", "progkey", "menukey", "paramkey",
    "alarmkey", "auxkey", "mkey", "tkey", "key0", "key1", "key2", "key3", "key4", "key5", "key6", "key7",
    "key8", "key9", "backey", "kihkey", "jqpkey"
];

const button_labels = [
    "RESET", "CURSOR UP", "CURSOR DOWN", "PAGE UP", "PAGE DOWN", "ALTER", "INSERT", "DELETE", "/.# EOB",
    "CAN", "INPUT", "OUTPUT START", "POS", "PROGRAM", "MENU OFFSET", "DGNOS PARAM", "OPR ALARM",
    "AUX GRAPH", "- M", "/ T", "0 S", "1 U", "2 Down/W", "3 R", "4 Left/X", "5 Sin/Z", "6 Right/F",
    "7 O", "8 Up/N", "9 G", "BAC Back", "KIHY Next", "JQPV No."
];

const buttonGrid = document.getElementById('button-grid');

button_names.forEach((name, index) => {
    const button = document.createElement('button');
    button.id = name;
    button.textContent = button_labels[index];
    button.className = "mx-1 rounded bg-green-400 px-3 py-1 hover:bg-pink-300 transform transition-transform duration-100 hover:scale-110";
    buttonGrid.appendChild(button);
});
