import { ExpandMore as ExpandMoreIcon } from "@mui/icons-material";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  TableContainer,
  TableRow,
  TableHead,
  TableCell,
  Paper,
  Table,
  TableBody,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

export function PackageReferences(props) {
  const { t } = useTranslation("package", { keyPrefix: "PackageReferences" });
  const { references, service } = props;

  return (
    <div>
      <Accordion
        elevation={0}
        sx={{
          border: `1.5px solid ${grey[300]}`,
          "&:before": { display: "none" },
        }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h7">{t("references")}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {references.length === 0 ? (
            <Typography>{t("noReferences")}</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 900 }}>{t("target")}</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>{t("version")}</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>{t("service")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {references.map(
                    (ref) =>
                      ref.service === service?.service_name && (
                        <TableRow key={ref.service + "-" + ref.target + "-" + ref.version}>
                          <TableCell component="th" scope="row">
                            {ref.target}
                          </TableCell>
                          <TableCell>{ref.version}</TableCell>
                          <TableCell>{ref.service}</TableCell>
                        </TableRow>
                      ),
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </AccordionDetails>
      </Accordion>
    </div>
  );
}

PackageReferences.propTypes = {
  references: PropTypes.arrayOf(PropTypes.object).isRequired,
  service: PropTypes.object.isRequired,
};
