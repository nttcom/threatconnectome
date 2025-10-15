import SearchIcon from "@mui/icons-material/Search";
import { InputAdornment, TextField } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState, useEffect } from "react";
import { isValidCVEFormat } from "../../utils/vulnUtils";

export function CVESearchField({ word, onApply, variant = "default" }) {
  const [newWord, setNewWord] = useState("");
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    setNewWord(word);
  }, [word]);

  const handleApply = (value) => {
    const trimmedValue = value.trim();
    const success = isValidCVEFormat(trimmedValue);
    if (!success) {
      enqueueSnackbar(
        "Invalid CVE ID format. Expected: CVE-YYYY-NNNN... (YYYY: 4 digits, NNNN...: 4 or more digits)",
        {
          variant: "error",
        },
      );
      return;
    }
    onApply(trimmedValue);
  };

  const mobileSx = {
    borderRadius: "12px",
    backgroundColor: "background.paper",
    "& fieldset": {
      borderColor: "rgba(0, 0, 0, 0.2)",
    },
  };
  const defaultSx = {};

  return (
    <TextField
      size="small"
      type="search"
      placeholder="Search CVE ID"
      hiddenLabel
      fullWidth
      value={newWord}
      onChange={(event) => setNewWord(event.target.value)}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          handleApply(event.target.value);
        }
      }}
      sx={{
        "& .MuiOutlinedInput-root": variant === "mobile" ? mobileSx : defaultSx,
      }}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        },
      }}
    />
  );
}

CVESearchField.propTypes = {
  word: PropTypes.string.isRequired,
  onApply: PropTypes.func.isRequired,
  variant: PropTypes.oneOf(["default", "mobile"]),
};
