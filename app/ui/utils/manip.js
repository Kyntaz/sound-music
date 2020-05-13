class CompoundManipulator {
    
    constructor(type, parent) {
        this.parent = parent;
        this.type = type;
        this.children = [];
    }

    add(type) {
        this.children.push(type);
    }

    change(ind, type) {
        this.children[ind] = type;
    }

    clear()  {
        this.children = [];
    }

    remove(ind) {
        this.children.splice(ind, 1);
    }

    setType(type) {
        this.type = type;
    }

    get(ind) {
        return this.children[ind];
    }

    toJson() {
        const children_json = []
        this.children.forEach(c => {
            if (typeof c === "string") {
                children_json.push(c);
            }
            else {
                children_json.push(c.toJson());
            }
        });
        return [this.type].concat(children_json);
    }
}

let manipulatorList;
let editableManip;

eel.manipulators()(l => {
    manipulatorList = l;
    editableManip = new CompoundManipulator(manipulatorList[1][0], null);
});