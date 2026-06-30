import { ExpandMore as ExpandMoreIcon } from "@mui/icons-material";
import {
  Accordion,
  AccordionDetails,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  AccordionSummary,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useTranslation } from "react-i18next";

import type { PackageReference, PackageReferenceService } from "./PackagePageTypes";

type PackageReferencesProps = {
  references: Array<PackageReference>;
  service?: PackageReferenceService;
};

export function PackageReferences({ references, service }: PackageReferencesProps) {
  const { t } = useTranslation("package", { keyPrefix: "PackageReferences" });

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
          <Typography variant="subtitle1">{t("references")}</Typography>
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
