let createMenuForm = document.currentScript.getAttribute("data-form-id");
let nameDisplayDiv = document.currentScript.getAttribute(
	"data-name-container-id"
);
let createMenuFormTimeOut = null;

const returnSafeHTMLFromInput = (input) => {
	if (input.value) {
		return $(input.value)[0].outerHTML;
	}
	return "";
};

$(() => {
	createMenuForm = document.getElementById(createMenuForm);
	nameDisplayDiv = document.getElementById(nameDisplayDiv);

	let prependedTextInput = document.querySelector(
		`#${createMenuForm.id} input#id_prepended_text`
	);
	let nameTextInput = document.querySelector(
		`#${createMenuForm.id} input#id_name`
	);
	let appendedTextInput = document.querySelector(
		`#${createMenuForm.id} input#id_appended_text`
	);
	prependedTextInput.addEventListener("keyup", (e) => {
		if (e.key == "/") {
			let input = e.target;
			input.value = `${input.value}/`;
		}
	});
	appendedTextInput.addEventListener("keyup", (e) => {
		if (e.key == "/") {
			let input = e.target;
			input.value = `${input.value}/`;
		}
	});

	createMenuForm.addEventListener("change", (e) => {
		clearTimeout(createMenuFormTimeOut);
		createMenuFormTimeOut = setTimeout(() => {
			nameDisplayDiv.innerHTML = `${prependedTextInput.value} ${nameTextInput.value} ${appendedTextInput.value}`;
		}, 800);
	});
});
