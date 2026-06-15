/* eslint-disable react/prop-types, jsx-a11y/no-autofocus */
import CheckIcon from "@mui/icons-material/Check";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import ImageIcon from "@mui/icons-material/Image";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Card, CardContent, Chip, Stack, TextField, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { maxDescriptionLengthInHalf, maxServiceNameLengthInHalf } from "../../../utils/const";
import { collapseSpaces } from "../../../utils/displayText";
import { getLengthError, getTagsError } from "../../../utils/SBOMManagement/formValidation";
import { normalizeTags } from "../../../utils/SBOMManagement/sbomManagementUtils";

import { ServiceIdCopyButton } from "./ServiceIdCopyButton";
import { AccordionHeader, AppButton, HeaderActionButton } from "./sharedUiParts";
import { fieldSx, floatingSurfaceSx, labelSx, slate, statusCardSx, uiRadii } from "./styleTokens";

function SbomImage({ editing, imageUrl, onImageUpload, onRemoveImage, title }) {
  const { t } = useTranslation("status", { keyPrefix: "DetailsPanel" });
  const [confirmingRemove, setConfirmingRemove] = useState(false);
  const imageInputRef = useRef(null);

  const openImagePicker = () => {
    setConfirmingRemove(false);
    imageInputRef.current?.click();
  };

  const imageInput = (
    <Box
      accept="image/*"
      component="input"
      onChange={onImageUpload}
      ref={imageInputRef}
      sx={{ display: "none" }}
      type="file"
    />
  );

  if (!imageUrl) {
    return (
      <Box
        sx={{
          alignItems: "center",
          bgcolor: slate[50],
          borderBottom: `1px dashed ${slate[300]}`,
          color: slate[400],
          display: "flex",
          height: 192,
          justifyContent: "center",
          position: "relative",
        }}
      >
        {imageInput}
        <Box sx={{ textAlign: "center" }}>
          <ImageIcon sx={{ fontSize: 32, mb: 1 }} />
          <Typography sx={{ fontSize: 14 }}>{t("imageNotSet")}</Typography>
          {editing && (
            <AppButton
              onClick={openImagePicker}
              size="small"
              startIcon={<UploadFileIcon />}
              sx={{ bgcolor: "white", mt: 1.5 }}
              variant="outlined"
            >
              {t("uploadImage")}
            </AppButton>
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        borderBottom: `1px solid ${slate[200]}`,
        height: 192,
        overflow: "hidden",
        position: "relative",
      }}
    >
      {imageInput}
      <Box
        alt={
          title ? t("sbomImageAltWithTitle", { title: collapseSpaces(title) }) : t("sbomImageAlt")
        }
        component="img"
        src={imageUrl}
        sx={{ height: "100%", objectFit: "cover", width: "100%" }}
      />
      <Box
        sx={{
          background: "linear-gradient(to top, rgba(0,0,0,0.45), rgba(0,0,0,0.1), transparent)",
          inset: 0,
          position: "absolute",
        }}
      />

      {editing && !confirmingRemove && (
        <Stack
          direction="row"
          flexWrap="wrap"
          justifyContent="flex-end"
          sx={{ gap: 1, position: "absolute", right: 12, top: 12 }}
        >
          <AppButton
            onClick={openImagePicker}
            size="small"
            startIcon={<UploadFileIcon />}
            sx={{ bgcolor: "rgba(255,255,255,0.95)" }}
            variant="outlined"
          >
            {t("changeImage")}
          </AppButton>
          <AppButton
            onClick={() => setConfirmingRemove(true)}
            size="small"
            startIcon={<DeleteIcon />}
            sx={{ bgcolor: "rgba(255,255,255,0.95)", color: slate[700] }}
            variant="outlined"
          >
            {t("delete")}
          </AppButton>
        </Stack>
      )}

      {confirmingRemove && (
        <Box
          sx={{
            bgcolor: "white",
            border: `1px solid ${slate[200]}`,
            borderRadius: uiRadii.field,
            ...floatingSurfaceSx,
            left: 12,
            p: 1.5,
            position: "absolute",
            right: 12,
            top: 12,
            zIndex: 1,
          }}
        >
          <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 700 }}>
            {t("confirmRemoveImageTitle")}
          </Typography>
          <Typography sx={{ color: slate[500], fontSize: 12, lineHeight: "20px", mt: 0.5 }}>
            {t("confirmRemoveImageBody")}
          </Typography>
          <Stack direction="row" sx={{ gap: 1, mt: 1.5 }}>
            <AppButton
              onClick={() => setConfirmingRemove(false)}
              size="small"
              sx={{ flex: 1 }}
              variant="outlined"
            >
              {t("cancel")}
            </AppButton>
            <AppButton
              onClick={() => {
                onRemoveImage();
                setConfirmingRemove(false);
              }}
              size="small"
              sx={{ flex: 1 }}
            >
              {t("confirmDelete")}
            </AppButton>
          </Stack>
        </Box>
      )}

      <Box sx={{ bottom: 16, left: 16, position: "absolute", right: 16 }}>
        <Typography
          sx={{
            color: "rgba(255,255,255,0.7)",
            fontSize: 12,
            fontWeight: 600,
            textTransform: "uppercase",
          }}
        >
          {t("image")}
        </Typography>
        <Typography noWrap sx={{ color: "white", fontSize: 16, fontWeight: 700, mt: 0.5 }}>
          {collapseSpaces(title) || t("untitledSbom")}
        </Typography>
      </Box>
    </Box>
  );
}

function DetailsForm({ editing, onUpdate, open, sbom }) {
  const { t } = useTranslation("status", { keyPrefix: "DetailsPanel" });
  const { enqueueSnackbar } = useSnackbar();
  const [tagsText, setTagsText] = useState(sbom.tags.join(", "));
  const [titleInput, setTitleInput] = useState(sbom.title);
  const isTitleBlank = editing && !titleInput.trim();

  const showInputError = (message) => {
    enqueueSnackbar(message, { variant: "error" });
  };

  useEffect(() => {
    if (editing) {
      setTagsText(sbom.tags.join(", "));
      setTitleInput(collapseSpaces(sbom.title));
    }
    // Reset only when entering edit mode or switching SBOM; ignore live `tags` updates while typing.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editing, sbom.id]);

  const emptyText = (
    <Box component="span" sx={{ color: slate[400] }}>
      {t("notSet")}
    </Box>
  );
  const display = { md: "block", xs: open ? "block" : "none" };

  if (!editing) {
    return (
      <Stack sx={{ display, gap: 2 }}>
        <Box>
          <Typography sx={labelSx}>{t("title")}</Typography>
          <Box sx={{ alignItems: "center", display: "flex", gap: 0.5, mt: 0.75, minWidth: 0 }}>
            <Typography
              noWrap
              sx={{
                color: slate[800],
                flex: "0 1 auto",
                fontSize: 14,
                fontWeight: 700,
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {sbom.title ? collapseSpaces(sbom.title) : emptyText}
            </Typography>
            <ServiceIdCopyButton serviceId={sbom.id} />
          </Box>
        </Box>
        <Box>
          <Typography sx={labelSx}>{t("description")}</Typography>
          <Typography
            sx={{
              color: slate[700],
              fontSize: 14,
              lineHeight: "24px",
              mt: 0.75,
              whiteSpace: "pre-wrap",
            }}
          >
            {sbom.description || emptyText}
          </Typography>
        </Box>
        <Box>
          <Typography sx={labelSx}>{t("tags")}</Typography>
          {sbom.tags.length > 0 ? (
            <Stack direction="row" flexWrap="wrap" sx={{ gap: 1, mt: 1 }}>
              {sbom.tags.map((tag) => (
                <Chip
                  icon={<LocalOfferIcon />}
                  key={tag}
                  label={tag}
                  size="small"
                  sx={{ bgcolor: slate[100], color: slate[600], fontSize: 12, fontWeight: 600 }}
                />
              ))}
            </Stack>
          ) : (
            <Typography sx={{ color: slate[400], fontSize: 14, mt: 1 }}>{t("notSet")}</Typography>
          )}
        </Box>
      </Stack>
    );
  }

  return (
    <Stack sx={{ display, gap: 2 }}>
      <Box>
        <Typography component="label" sx={labelSx}>
          {t("title")}
        </Typography>
        <TextField
          fullWidth
          error={isTitleBlank}
          helperText={isTitleBlank ? t("serviceNameRequired") : undefined}
          onChange={(event) => {
            const nextTitle = event.target.value;
            const error = getLengthError(
              t,
              nextTitle,
              maxServiceNameLengthInHalf,
              "tooLongServiceName",
            );
            if (error) {
              showInputError(error);
              return;
            }

            setTitleInput(nextTitle);
            onUpdate({ title: nextTitle });
          }}
          placeholder={t("titlePlaceholder")}
          sx={{ ...fieldSx, mt: 1 }}
          value={titleInput}
        />
      </Box>
      <Box>
        <Typography component="label" sx={labelSx}>
          {t("description")}
        </Typography>
        <TextField
          fullWidth
          minRows={4}
          multiline
          onChange={(event) => {
            const nextDescription = event.target.value;
            const error = getLengthError(
              t,
              nextDescription,
              maxDescriptionLengthInHalf,
              "tooLongDescription",
            );
            if (error) {
              showInputError(error);
              return;
            }

            onUpdate({ description: nextDescription });
          }}
          placeholder={t("descriptionPlaceholder")}
          sx={{ ...fieldSx, mt: 1 }}
          value={sbom.description}
        />
      </Box>
      <Box>
        <Typography component="label" sx={labelSx}>
          {t("tags")}
        </Typography>
        <TextField
          fullWidth
          onChange={(event) => {
            const raw = event.target.value;
            const nextTags = normalizeTags(raw);
            const error = getTagsError(t, nextTags);
            if (error) {
              showInputError(error);
              return;
            }

            setTagsText(raw);
            onUpdate({ tags: nextTags });
          }}
          placeholder={t("tagsPlaceholder")}
          sx={{ ...fieldSx, mt: 1 }}
          value={tagsText}
        />
      </Box>
    </Stack>
  );
}

export function DetailsPanel({
  editing,
  imageUrl,
  onCommit,
  onImageUpload,
  onRemoveImage,
  onToggle,
  onUpdate,
  open,
  sbom,
}) {
  const { t } = useTranslation("status", { keyPrefix: "DetailsPanel" });

  return (
    <Card
      sx={{
        ...statusCardSx,
        overflow: "hidden",
      }}
    >
      <SbomImage
        editing={editing}
        imageUrl={imageUrl}
        onImageUpload={onImageUpload}
        onRemoveImage={onRemoveImage}
        title={sbom.title}
      />
      <AccordionHeader
        action={
          <HeaderActionButton
            active={editing}
            icon={editing ? CheckIcon : EditIcon}
            disabled={editing && !sbom.title.trim()}
            onClick={onCommit}
          >
            {editing ? t("done") : t("edit")}
          </HeaderActionButton>
        }
        icon={InfoOutlinedIcon}
        onToggle={onToggle}
        open={open}
        title={t("details")}
      />
      <CardContent
        sx={{
          display: { md: "block", xs: open ? "block" : "none" },
          minWidth: 0,
          pb: 1.5,
          pt: 0,
          px: 2,
        }}
      >
        <DetailsForm editing={editing} onUpdate={onUpdate} open={open} sbom={sbom} />
      </CardContent>
    </Card>
  );
}
