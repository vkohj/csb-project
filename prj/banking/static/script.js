function input(self) {
    if (self.value[2] != "-" && self.value[2] != undefined) {
        self.value = self.value.slice(0, 2) + "-" + self.value.slice(2);
    }

    if (self.value[7] != "-" && self.value[7] != undefined) {
        self.value = self.value.slice(0, 7) + "-" + self.value.slice(7);
    }
}

function historyTableOnLoad() {
    table = document.getElementById("table");
    logs = table.getElementsByTagName('tbody');
    
    if (logs.length > 0) {
        logs[0].classList.add("focus");
    }
}

function historyOnClick(o) {
    p = o.parentNode;
    if (p.classList.contains("focus")) {
        p.classList.remove("focus");
        return;
    }

    clearFocus();
    p.classList.add("focus");
}

function clearFocus() {
    table = document.getElementById("table");
    logs = table.getElementsByTagName('tbody');

    for (i=0; i < logs.length; i+=1) {
        logs[i].classList.remove("focus");
    }
}