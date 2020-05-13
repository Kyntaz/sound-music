class RandomManipulator extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            file: "",
            audio: null,
            progress: false,
            complexity: 10
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

    generateAudio() {
        this.setState({
            progress: true
        });
        eel.renderMakeRand(this.state.file, this.state.complexity)(p => {
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

    readFile() {
        eel.getFile()(f => {
            this.setState({
                file: f
            });
        });
    }

    setComplexity(c) {
        this.setState({
            complexity: c
        });
    }

    render() {
        return (
            <div className="d-flex flex-column justify-content-center h-100 bg-dark">
                <div className="container d-flex flex-column text-center mx-auto w-50 border p-3 bg-white shadow">
                    <button className="btn btn-light my-3" onClick={() => this.readFile()}>{this.state.file || "Select file..."}</button>
                    <div className="container border my-3 p-1">
                        <label htmlFor="complexity-input"> Complexity: </label>
                        <input value={this.state.complexity} type="range" className="custom-range my-0" min="1" max="20" id="complexity-input" onChange={e => this.setComplexity(parseInt(e.target.value))} />
                        <span className="badge badge-pill badge-primary mt-2"> {this.state.complexity} </span>
                    </div>
                    <button className="btn btn-success my-3" onClick={() => this.generateAudio()}>Go!</button>
                    {this.renderAudio()}
                </div>
            </div>
        );
    }
}