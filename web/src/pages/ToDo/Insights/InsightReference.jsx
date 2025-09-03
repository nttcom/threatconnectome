import ArticleIcon from "@mui/icons-material/Article";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Link,
  Typography,
  Divider,
} from "@mui/material";
import PropTypes from "prop-types";

export function InsightReference(props) {
  const { dataProcessingStrategy, insightReferences } = props;

  if (!insightReferences || insightReferences.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No analysis basis available.
      </Typography>
    );
  }

  return (
    <>
      <Box>
        <Typography variant="h6" gutterBottom>
          Data Processing Strategy
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {dataProcessingStrategy}
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" gutterBottom>
          Data Sources
        </Typography>
        <List dense>
          {insightReferences.map((reference, index) => (
            <ListItem key={index}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <ArticleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={
                  reference.url ? (
                    <span style={{ color: "#000", display: "inline-flex", alignItems: "center" }}>
                      {reference.link_text}
                      <Link
                        href={reference.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        underline="none"
                        sx={{
                          display: "inline-flex",
                          alignItems: "center",
                          ml: 0.5,
                        }}
                      >
                        <OpenInNewIcon fontSize="small" color="primary" />
                      </Link>
                    </span>
                  ) : (
                    <span style={{ color: "#000" }}>{reference.link_text}</span>
                  )
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </>
  );
}

InsightReference.propTypes = {
  dataProcessingStrategy: PropTypes.string.isRequired,
  insightReferences: PropTypes.arrayOf(PropTypes.object).isRequired,
};
