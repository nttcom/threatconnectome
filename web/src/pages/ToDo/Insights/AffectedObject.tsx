import { List, ListItem, ListItemIcon, ListItemText, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { AffectedObject as AffectedObjectType } from "../../../../types/types.gen";
import { objectCategoryIcons } from "./insightConst";

type AffectedObjectProps = {
  affectedObjects: AffectedObjectType[];
};

export function AffectedObject(props: AffectedObjectProps) {
  const { affectedObjects } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "Insights.AffectedObject" });

  if (!affectedObjects || affectedObjects.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        {t("noAssets")}
      </Typography>
    );
  }

  return (
    <>
      <Typography variant="h6" gutterBottom>
        {t("title")}
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
