import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Card,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

export function VulnSSVCElement(props) {
  const { title, titleDescription, values, value } = props;

  const filterValue = values.filter((item) => value === item.key)[0];
  const valueKey = filterValue.key;
  const valueDescription = filterValue.valueDescription;

  return (
    <Grid key={title} item xs={12} md={6}>
      <Card variant="outlined" sx={{ p: 3, height: "100%" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            mb: 1,
          }}
        >
          <Typography sx={{ fontWeight: "bold", pr: 0.5 }}>{title}</Typography>
          <Tooltip title={titleDescription}>
            <HelpOutlineOutlinedIcon color="action" fontSize="small" />
          </Tooltip>
        </Box>
        <ToggleButtonGroup color="primary" value={valueKey} sx={{ mb: 1 }}>
          {values.map((value) => (
            <ToggleButton key={value.key} value={value.key} disabled>
              {value.name}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        <Typography variant="body2" color="textSecondary">
          {valueDescription}
        </Typography>
      </Card>
    </Grid>
  );
}
VulnSSVCElement.propTypes = {
  title: PropTypes.string.isRequired,
  titleDescription: PropTypes.string.isRequired,
  values: PropTypes.array.isRequired,
  value: PropTypes.string.isRequired,
};
