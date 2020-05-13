class ManipulatorList extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            manips: []
        };

        eel.manipulators()(list => {
            this.setList([].concat(list[0], list[1]));
        });
    }

    setList(list) {
        this.setState({
            manips: list
        });
    }

    getList() {
        const manips = this.state.manips;
        let l = []
        manips.forEach(s => {
            l.push(e(
                'li',
                {
                    className: "list-group-item"
                },
                s
            ));
        });
        return l;
    }

    render() {
        return e(
            'ul',
            {
                className: "list-group"
            },
            this.getList()
        );
    }
}
