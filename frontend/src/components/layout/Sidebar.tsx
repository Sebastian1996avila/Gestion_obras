import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Theme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as ProyectosIcon,
  Inventory as MaterialesIcon,
  AccessTime as AsistenciaIcon,
  Payment as NominaIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  toggleDrawer: () => void;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Proyectos', icon: <ProyectosIcon />, path: '/proyectos' },
  { text: 'Materiales', icon: <MaterialesIcon />, path: '/materiales' },
  { text: 'Asistencia', icon: <AsistenciaIcon />, path: '/asistencia' },
  { text: 'Nómina', icon: <NominaIcon />, path: '/nomina' },
];

const Sidebar = ({ open }: SidebarProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? 240 : 64,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 240 : 64,
          boxSizing: 'border-box',
          transition: (theme: Theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          overflowX: 'hidden',
        },
      }}
    >
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            selected={location.pathname === item.path}
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: 2.5,
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 3 : 'auto',
                justifyContent: 'center',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              sx={{ 
                opacity: open ? 1 : 0,
                display: open ? 'block' : 'none'
              }} 
            />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar; 