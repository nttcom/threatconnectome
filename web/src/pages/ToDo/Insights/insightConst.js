import AlbumIcon from "@mui/icons-material/Album";
import ApartmentIcon from "@mui/icons-material/Apartment";
import BrokenImageIcon from "@mui/icons-material/BrokenImage";
import CloudOffIcon from "@mui/icons-material/CloudOff";
import DevicesOtherIcon from "@mui/icons-material/DevicesOther";
import DisabledVisibleIcon from "@mui/icons-material/DisabledVisible";
import DnsIcon from "@mui/icons-material/Dns";
import DomainDisabledIcon from "@mui/icons-material/DomainDisabled";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import InventoryIcon from "@mui/icons-material/Inventory";
import LaptopIcon from "@mui/icons-material/Laptop";
import NoEncryptionIcon from "@mui/icons-material/NoEncryption";
import PersonIcon from "@mui/icons-material/Person";
import RemoveModeratorIcon from "@mui/icons-material/RemoveModerator";
import DoNotTouchIcon from "@mui/icons-material/DoNotTouch";
import RouterIcon from "@mui/icons-material/Router";
import SmartphoneIcon from "@mui/icons-material/Smartphone";
import VideogameAssetIcon from "@mui/icons-material/VideogameAsset";
import VideogameAssetOffIcon from "@mui/icons-material/VideogameAssetOff";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";

export const impactCategoryIcons = {
  damage_to_property: { icon: BrokenImageIcon, text: "Damage to Property" },
  denial_of_control: { icon: DoNotTouchIcon, text: "Denial of Control" },
  denial_of_view: { icon: DisabledVisibleIcon, text: "Denial of View" },
  loss_of_availability: { icon: CloudOffIcon, text: "Loss of Availability" },
  loss_of_control: { icon: VideogameAssetOffIcon, text: "Loss of Control" },
  loss_of_productivity_and_revenue: {
    icon: DomainDisabledIcon,
    text: "Loss of Productivity and Revenue",
  },
  loss_of_protection: { icon: RemoveModeratorIcon, text: "Loss of Protection" },
  loss_of_safety: { icon: NoEncryptionIcon, text: "Loss of Safety" },
  loss_of_view: { icon: VisibilityOffIcon, text: "Loss of View" },
  manipulation_of_control: { icon: VideogameAssetIcon, text: "Manipulation of Control" },
  manipulation_of_view: { icon: VisibilityIcon, text: "Manipulation of View" },
  theft_of_operational_information: {
    icon: FileCopyIcon,
    text: "Theft of Operational Information",
  },
};

export const objectCategoryIcons = {
  server: DnsIcon,
  client_device: LaptopIcon,
  mobile_device: SmartphoneIcon,
  network_device: RouterIcon,
  storage: InventoryIcon,
  iot_device: DevicesOtherIcon,
  physical_media: AlbumIcon,
  facility: ApartmentIcon,
  person: PersonIcon,
};
