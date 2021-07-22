/**
 * Scrolls to bottom.
 *
 * @param {React.MutableRefObject} ref Reference object to scroll.
 */
export const scrollToBottom = (ref) => {
	const element = ref.current;
	element.scrollTop = element.scrollHeight;
};

export default scrollToBottom;
