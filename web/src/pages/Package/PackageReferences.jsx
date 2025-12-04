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

export function PackageReferences(props) {
  const { references, serviceDict } = props;

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
          <Typography variant="h7">References</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {references.length === 0 ? (
            <Typography>no references</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 900 }}>target</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>version</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>Service</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {references.map(
                    (ref) =>
                      ref.service === serviceDict?.service_name && (
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
  serviceDict: PropTypes.object.isRequired,
};
