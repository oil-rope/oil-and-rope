import React, { Suspense } from "react";
import ReactDOM from "react-dom";
import Loader from "./components/loader/Loader";

import { Provider } from "react-redux";
import store from "./store";

const TreeView = React.lazy(() =>
	import("./components/treeView/TreeView")
);

let treeView = document.getElementById("treeView");
if (treeView != null) {

	const App = () => {
		return (
			<Provider store={store}>
				<Suspense fallback={<Loader />}>
					<TreeView />
				</Suspense>
			</Provider>
		);
	};

	ReactDOM.render(<App />, treeView);
}
