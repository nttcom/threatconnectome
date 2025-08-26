import ArticleIcon from "@mui/icons-material/Article";
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
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
                    <a
                      href={reference.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: "#1976d2",
                        textDecoration: "underline",
                        cursor: "pointer",
                        fontWeight: 500,
                      }}
                      onMouseOver={(e) => (e.currentTarget.style.color = "#1565c0")}
                      onFocus={(e) => (e.currentTarget.style.color = "#1565c0")}
                      onMouseOut={(e) => (e.currentTarget.style.color = "#1976d2")}
                      onBlur={(e) => (e.currentTarget.style.color = "#1976d2")}
                    >
                      {reference.link_text}
                    </a>
                  ) : (
                    <>{reference.link_text}</>
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
