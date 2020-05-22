class UiEvolutionary extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            audio1: "",
            audio2: "",
            best: "",
            file: "",

            in_progress: false,
            reproduction_cycle: 5,
            complexity: 3,
            population: 10,
            mutation: 0.1,
            elitism: 0.5
        };
    }

    setReproduction(v) {
        this.setState({reproduction_cycle: v});
    }

    setComplexity(v) {
        this.setState({complexity: v});
    }

    setPopulation(v) {
        this.setState({population: v});
    }

    setMutation(v) {
        this.setState({mutation: v});
    }

    setElitism(v) {
        this.setState({elitism: v});
    }

    readFile() {
        eel.getFile()(f => {
            this.setState({
                file: f
            });
        });
    }

    start() {
        this.setState({
            in_progress: true
        });

        eel.ievolve_start(
            this.state.file,
            this.state.reproduction_cycle,
            this.state.complexity,
            this.state.population,
            this.state.mutation,
            this.state.elitism
        )(audios => {
            this.setState({
                audio1: audios[0],
                audio2: audios[1],
                in_progress: false
            });
        });
    }

    step(w) {
        this.setState({
            in_progress: true
        });

        eel.ievolve_step(w)(audios => {
            this.setState({
                audio1: audios[0],
                audio2: audios[1],
            });

            eel.ievolve_best()(audio => {
                this.setState({
                    best: audio,
                    in_progress: false
                });
            });
        });
    }

    render_start() {
        return (
            <div className="d-flex flex-column justify-content-center h-100 bg-dark">
                <div className="container d-flex flex-column text-center mx-auto w-50 border p-3 bg-white shadow">
                    <button className="btn btn-light my-3" onClick={() => this.readFile()}>{this.state.file || "Select file..."}</button>
                    <button className="btn btn-success my-3" onClick={() => this.start()}>Go!</button>
                </div>
            </div>
        );
    }

    render_step() {
        return (
            <div className="d-flex flex-column justify-content-center h-100 bg-dark">
                <div className="container d-flex flex-column text-center mx-auto w-50 border p-3 bg-white shadow">
                    <audio key="audio" className="mx-auto" controls>
                        <source src={this.state.audio1} />
                    </audio>
                    <button className="btn btn-success my-3" onClick={() => this.step(0)}>1</button>
                    <audio key="audio" className="mx-auto" controls>
                        <source src={this.state.audio2} />
                    </audio>
                    <button className="btn btn-success my-3" onClick={() => this.step(1)}>2</button>
                    <h3> Best so far: </h3>
                    <audio key="audio" className="mx-auto" controls>
                        <source src={this.state.best} />
                    </audio>
                </div>
            </div>
        );
    }

    render_progress() {
        return (
            <div className="d-flex flex-column justify-content-center h-100 bg-dark">
                <div className="container d-flex flex-column text-center mx-auto w-50 border p-3 bg-white shadow">
                    <div className="spinner-border mx-auto my-5">
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>
            </div>
        );
    }

    render() {
        if (this.state.in_progress) return this.render_progress()
        else if (this.state.audio1 !== "" && this.state.audio2 !== "") return this.render_step()
        else return this.render_start()
    }
}