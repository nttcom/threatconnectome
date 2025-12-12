import parsePhoneNumber from "libphonenumber-js";

export const maskPhoneNumber = (inputPhoneNumber) => {
  const phoneNumber = parsePhoneNumber(inputPhoneNumber);

  if (phoneNumber && phoneNumber.isValid()) {
    const countryCode = `+${phoneNumber.countryCallingCode}`;
    const nationalNumber = phoneNumber.nationalNumber;
    const lastFourDigits = nationalNumber.slice(-4);
    return `${countryCode} ${"*".repeat(nationalNumber.length - 4)}${lastFourDigits}`;
  } else {
    return "N/A";
  }
};
