// eslint-disable-next-line import/no-named-as-default
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

export const isE164Format = (inputPhoneNumber) => {
  const phoneNumber = parsePhoneNumber(inputPhoneNumber);
  if (phoneNumber && phoneNumber.isValid() && phoneNumber.format("E.164") === inputPhoneNumber) {
    return true;
  } else {
    return false;
  }
};

export const normalizePhoneNumberToE164 = (inputPhoneNumber, defaultCountry) => {
  const phoneNumber = parsePhoneNumber(inputPhoneNumber, defaultCountry);

  if (phoneNumber && phoneNumber.isValid()) {
    return phoneNumber.format("E.164");
  }

  return null;
};

export const getNationalPhoneNumber = (inputPhoneNumber, defaultCountry) => {
  const phoneNumber = parsePhoneNumber(inputPhoneNumber, defaultCountry);

  if (phoneNumber && phoneNumber.isValid()) {
    return phoneNumber.nationalNumber;
  }

  return null;
};
