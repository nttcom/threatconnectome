import PropTypes from "prop-types";

export const pageItemType = PropTypes.shape({
  icon: PropTypes.elementType.isRequired,
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  shortLabel: PropTypes.string,
  tone: PropTypes.string.isRequired,
});

export const teamItemType = PropTypes.shape({
  current: PropTypes.bool,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
});

export const labelsType = PropTypes.shape({
  createTeam: PropTypes.string.isRequired,
  current: PropTypes.string.isRequired,
  currentTeamDetail: PropTypes.string.isRequired,
  homeAriaLabel: PropTypes.string.isRequired,
  logout: PropTypes.string.isRequired,
  noTeam: PropTypes.string.isRequired,
  pageMenu: PropTypes.string.isRequired,
  pageSwitch: PropTypes.string.isRequired,
  settings: PropTypes.string.isRequired,
  teamMenu: PropTypes.string.isRequired,
  teamSelect: PropTypes.string.isRequired,
  userMenu: PropTypes.string.isRequired,
});
