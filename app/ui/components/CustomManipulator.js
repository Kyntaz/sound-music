class CustomManipulator extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            progress: false,
            audio: null,
            file: null,
            editing: null
        };
    }

    renderAudio() {
        if (this.state.audio != null && !this.state.progress) {
            return (
                <audio key="audio" className="mx-auto" controls>
                    <source src={this.state.audio} />
                </audio>
            );
        }
        else if (!this.state.progress) {
            return (
                <p key="audio"> No audio generated... </p>
            );
        }
        else {
            return (
                <div className="spinner-border mx-auto">
                    <span class="sr-only">Loading...</span>
                </div>
            );
        }
    }

    edit(manip) {
        this.setState({
            editing: manip
        });
    }

    readFile() {
        eel.getFile()(f => {
            this.setState({
                file: f
            });
        });
    }

    generateAudio() {
        this.setState({
            progress: true
        });
        eel.renderCustom(this.state.file, editableManip.toJson())(p => {
            if (p === "") {
                this.setState({
                    audio: null,
                    progress: false
                })
                return
            }
            this.setState({
                audio: p,
                progress: false
            });
        });
    }

    notEditingState() {
        return (
            <div className="container d-flex flex-column text-center mx-auto w-50 border p-3 bg-white shadow">
                <button className="btn btn-light my-1" onClick={() => this.readFile()}>{this.state.file || "Select file..."}</button>
                <button className="btn btn-warning my-1" onClick={() => this.edit(editableManip)}> Edit </button>
                <button className="btn btn-success my-5" onClick={() => this.generateAudio()}>Go!</button>
                {this.renderAudio()}
            </div>
        );
    }

    manipOptions(c, i) {
        const opts = [];
        manipulatorList[0].forEach(manip => {
            opts.push(
                <option>{manip}</option>
            );
        });
        return (
            <select value={c} className="form-control input-group-prepend" style={{borderTopRightRadius: 0, borderBottomRightRadius: 0}} onChange={e => {
                this.state.editing.change(i, e.target.value);
                this.forceUpdate();
            }}>
                {opts}
            </select>
        );
    }

    compManipOptions(c, i) {
        const opts = [];
        manipulatorList[1].forEach(manip => {
            opts.push(
                <option>{manip}</option>
            );
        });
        return (
            <select value={c} className="form-control input-group-prepend" style={{borderTopRightRadius: 0, borderBottomRightRadius: 0}} onChange={e => {
                this.state.editing.get(i).setType(e.target.value);
                this.forceUpdate();
            }}>
                {opts}
            </select>
        );
    }

    getManipPath() {
        let pstr = this.state.editing.type;
        let manip = this.state.editing.parent;
        while (!(manip === null)) {
            pstr = "".concat(manip.type, " / ", pstr);
            manip = manip.parent;
        }
        return (
            <p className="lead">{pstr}</p>
        );
    }

    editingState() {
        const childEls = [];
        this.state.editing.children.forEach((c,i) => {
            let el;
            if (typeof c === "string") {
                let name = c;
                el = (
                    <li className="list-group-item d-flex flex-row">
                        {this.manipOptions(name, i)}
                        <button className="btn btn-danger" style={{borderTopLeftRadius: 0, borderBottomLeftRadius: 0}} onClick={() => {
                            this.state.editing.remove(i);
                            this.forceUpdate();
                        }}> Remove </button>
                    </li>
                );
            }
            else {
                let name = c.type;
                el = (
                    <li className="list-group-item d-flex flex-row">
                        {this.compManipOptions(name, i)}
                        <button className="btn btn-warning" style={{borderTopLeftRadius: 0, borderBottomLeftRadius: 0}} onClick={() => {
                            this.setState({
                                editing: this.state.editing.get(i)
                            });
                        }}> Edit </button>
                        <button className="btn btn-danger" style={{borderTopLeftRadius: 0, borderBottomLeftRadius: 0}} onClick={() => {
                            this.state.editing.remove(i);
                            this.forceUpdate();
                        }}> Remove </button>
                    </li>
                );
            }
            childEls.push(el);
        });

        return (
            <div className="container d-flex flex-column text-center mx-auto w-50 border px-3 pt-3 bg-white shadow" style={{maxHeight: "70vh", overflowY: 'scroll'}}>
                {this.getManipPath()}
                <ul className="list-group list-group-flush">
                    {childEls}
                </ul>
                <div className="btn-group">
                    <button className="btn btn-success" style={{borderTopLeftRadius: 0, borderTopRightRadius: 0}} onClick={() => {
                        this.state.editing.add(manipulatorList[0][0]);
                        this.forceUpdate();
                    }}> Add </button>
                    <button className="btn btn-info" style={{borderTopLeftRadius: 0, borderTopRightRadius: 0}} onClick={() => {
                        this.state.editing.add(new CompoundManipulator(manipulatorList[1][0], this.state.editing));
                        this.forceUpdate();
                    }}> Add Compound </button>
                </div>
                <div className="btn-group my-3">
                    <button className="btn btn-warning" onClick={() => this.edit(this.state.editing.parent)}> Back </button>
                    <button className="btn btn-danger" onClick={() => {this.state.editing.clear(); this.forceUpdate()}}> Clear </button>
                    <button className="btn btn-success" onClick={() => this.edit(null)}> Done </button>
                </div>
            </div>
        );
    }

    render() {
        const inner = this.state.editing === null ? this.notEditingState() : this.editingState();
        return (
            <div className="d-flex flex-column justify-content-center h-100 bg-dark">
                {inner}
            </div>
        );
    }
}