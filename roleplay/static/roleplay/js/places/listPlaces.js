const url = document.currentScript.getAttribute("place-api-url");
let element = document.currentScript.getAttribute("source-view-element");
// Random ID so never conflicts
const loadingId = Math.round(Math.random() * 100);
const loadingElement = `<div id="${loadingId}" class="spinner-border" role="status"><span class="sr-only">Loading...</span></div>`;

$(() => {
	element = document.querySelector(element);
	// Loading...
	$(element).parent().prepend(loadingElement);
	const height = $(element).height();
	const width = $(element).width();

	// Selecting de SVG element for D3 and setting Height and Width
	const svg = d3.select(element);
	// Margin convention
	const margin = { top: 0, right: 150, bottom: 0, left: 70 };
	const innerWidth = width - margin.left - margin.right;
	const innerHeight = height - margin.bottom - margin.top;
	const tree = d3.tree().size([innerHeight, innerWidth]);

	const zoomG = svg.attr("width", width).attr("height", height).append("g");

	const g = zoomG
		.append("g")
		.attr("transform", `translate(${margin.left}, ${margin.top})`);

	svg.call(
		d3.zoom().on("zoom", () => {
			zoomG.attr("transform", d3.event.transform);
		})
	);

	// GET from API
	fetch(url)
		.then((response) => response.json())
		.then((data) => {
			// Loaded!
			$(`#${loadingId}`).remove();

			const root = d3.hierarchy(data);
			const links = tree(root).links();
			const linkPathGenerator = d3
				.linkHorizontal()
				.x((d) => d.y)
				.y((d) => d.x);

			g.selectAll("path")
				.data(links)
				.enter()
				.append("path")
				.attr("d", linkPathGenerator);

			g.selectAll("text")
				.data(root.descendants())
				.enter()
				.append("text")
				.attr("x", (d) => d.y)
				.attr("y", (d) => d.x)
				.attr("dy", () => "0.32em")
				// Tex align Middle for everything except leaf
				.attr("text-anchor", (d) => (d.children ? "middle" : "start"))
				// Font size from bigger to smaller
				.attr("font-size", (d) => `${3.25 - d.depth}rem`)
				// Text itself
				.text((d) => d.data.name);
		});
});
