const { DateTime } = require("luxon");
const { dateFormat } = require("./constants");

const validateDateString= date => {
    const dateString = getDateFromString(date).toFormat(dateFormat);
    return date === dateString;
}

const validateTimeString = timeString => {
    const timeArray = timeString.split(':');
    const a = DateTime.fromObject({ hour: timeArray[0], minute: timeArray[1] }).toFormat('HH:mm');
    console.log('datetime', a, timeString);
    return DateTime.fromObject({ hour: timeArray[0], minute: timeArray[1] }).toFormat('HH:mm') === timeString;
}

const getDateFromString = dateString => {
    const dateArray = dateString.split('-');

    return DateTime.fromObject({ year: dateArray[0], month: dateArray[1], day: dateArray[2]});
}


const fillPlaceholdersInText = (text, ...placeholders) => {
    const placeholderArray = placeholders || [];
    let filledText = text;

    placeholderArray.forEach((element, index) => {
        filledText = filledText.replace(new RegExp(`\\{${index}\\}`, 'g'), element);
    });

    return filledText;
}


module.exports = {
    fillPlaceholdersInText,
    getDateFromString,
    validateDateString,
    validateTimeString,
}
