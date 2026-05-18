// eslint-disable-next-line import/no-named-as-default
import parsePhoneNumber, { type CountryCode, type PhoneNumber } from "libphonenumber-js";

type PhoneNumberInput = string | null | undefined;

const safeParsePhoneNumber = (
  inputPhoneNumber: PhoneNumberInput,
  defaultCountry?: CountryCode,
): PhoneNumber | null => {
  if (typeof inputPhoneNumber !== "string") {
    return null;
  }

  try {
    return parsePhoneNumber(inputPhoneNumber, defaultCountry) ?? null;
  } catch {
    return null;
  }
};

export const maskPhoneNumber = (inputPhoneNumber: PhoneNumberInput): string => {
  const phoneNumber = safeParsePhoneNumber(inputPhoneNumber);

  if (phoneNumber && phoneNumber.isValid()) {
    const countryCode = `+${phoneNumber.countryCallingCode}`;
    const nationalNumber = phoneNumber.nationalNumber;
    const lastFourDigits = nationalNumber.slice(-4);
    return `${countryCode} ${"*".repeat(nationalNumber.length - 4)}${lastFourDigits}`;
  } else {
    return "N/A";
  }
};

export const isE164Format = (inputPhoneNumber: PhoneNumberInput): boolean => {
  const phoneNumber = safeParsePhoneNumber(inputPhoneNumber);
  if (phoneNumber && phoneNumber.isValid() && phoneNumber.format("E.164") === inputPhoneNumber) {
    return true;
  } else {
    return false;
  }
};

export const normalizePhoneNumberToE164 = (
  inputPhoneNumber: PhoneNumberInput,
  defaultCountry?: CountryCode,
): string | null => {
  const phoneNumber = safeParsePhoneNumber(inputPhoneNumber, defaultCountry);

  if (phoneNumber && phoneNumber.isValid()) {
    return phoneNumber.format("E.164");
  }

  return null;
};

export const getNationalPhoneNumber = (
  inputPhoneNumber: PhoneNumberInput,
  defaultCountry?: CountryCode,
): string | null => {
  const phoneNumber = safeParsePhoneNumber(inputPhoneNumber, defaultCountry);

  if (phoneNumber && phoneNumber.isValid()) {
    return phoneNumber.nationalNumber;
  }

  return null;
};
