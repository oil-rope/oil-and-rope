import moment from "moment";

/**
 * Transform date into desired format.
 *
 * @param {Date} date The date to parse.
 */
export const formatDate = (date, format = "DD/MM/YYYY HH:mm:ss") => {
  return moment(date).format(format);
};
