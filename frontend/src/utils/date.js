import dayjs from "dayjs";

/**
 * Transform date into desired format.
 *
 * @param {Date} date The date to parse.
 */
export const formatDate = (date, format = "DD/MM/YYYY HH:mm:ss") => {
	return dayjs(date).format(format);
};
