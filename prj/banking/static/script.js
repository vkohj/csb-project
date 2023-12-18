function input(self) {
    if (self.value[2] != "-" && self.value[2] != undefined) {
        self.value = self.value.slice(0, 2) + "-" + self.value.slice(2);
    }

    if (self.value[7] != "-" && self.value[7] != undefined) {
        self.value = self.value.slice(0, 7) + "-" + self.value.slice(7);
    }
}