import { List, ListItem, ListItemIcon, ListItemText, Typography } from "@mui/material";
import PropTypes from "prop-types";

import { objectCategoryIcons } from "./insightConst.js";

export function AffectedObject(props) {
  const { affectedObjects } = props;

  if (!affectedObjects || affectedObjects.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No affected assets available.
      </Typography>
    );
  }

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Potentially Affected Assets
      </Typography>
      <List>
        {affectedObjects.map((object, index) => (
          <ListItem key={index} divider={index < affectedObjects.length - 1}>
            <ListItemIcon sx={{ minWidth: 40 }}>
              {(() => {
                const ObjectCategoryIcon = objectCategoryIcons[object.object_category];
                return ObjectCategoryIcon ? <ObjectCategoryIcon /> : null;
              })()}
            </ListItemIcon>
            <ListItemText primary={object.name} secondary={object.description} />
          </ListItem>
        ))}
      </List>
    </>
  );
}

AffectedObject.propTypes = {
  affectedObjects: PropTypes.object.isRequired,
};
