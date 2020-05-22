class ModeSelector extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            mode: <Help />
        };
    }

    setMode(nMode) {
        this.setState({
            mode: nMode
        });
    }

    makeModes() {
        const modes = {
            "Random Manipulation": <RandomManipulator />,
            "Custom Manipulation": <CustomManipulator />,
            "Interactive Evolution": <UiEvolutionary />,
            "Help": <Help />
        };

        let out = [];

        Object.keys(modes).forEach(key => {
            out.push(
                <li className="nav-item">
                    <a className={"nav-link mode-selector-option" + (key === "Help" ? " active" : "")} href="#" onClick={(e) => {
                        this.setMode(modes[key]);
                        document.querySelectorAll(".mode-selector-option").forEach(l => {
                            l.className = "nav-link mode-selector-option";
                        });
                        e.target.className = "nav-link mode-selector-option active";
                    }}>
                        {key}
                    </a>
                </li>
            );
        });
        return out;
    }

    render() {
        return (
            <div>
                <ul className="nav nav-pills nav-fill">
                    {this.makeModes()}
                </ul>
                {this.state.mode}
            </div>
        );
    }
}