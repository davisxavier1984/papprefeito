/**
 * Botão de alternância de tema (Claro / Escuro / Sistema).
 * Padrão "Sistema" segue o SO; a escolha manual é persistida.
 */
import React from 'react';
import { Dropdown, Button } from 'antd';
import type { MenuProps } from 'antd';
import { BulbOutlined, BulbFilled, DesktopOutlined } from '@ant-design/icons';
import { useThemeStore, type ThemeMode } from '../../stores/themeStore';

const ThemeToggle: React.FC = () => {
  const mode = useThemeStore((s) => s.mode);
  const isDark = useThemeStore((s) => s.isDark);
  const setMode = useThemeStore((s) => s.setMode);

  const triggerIcon =
    mode === 'system' ? <DesktopOutlined /> : isDark ? <BulbFilled /> : <BulbOutlined />;

  const items: MenuProps['items'] = [
    { key: 'light', icon: <BulbOutlined />, label: 'Claro' },
    { key: 'dark', icon: <BulbFilled />, label: 'Escuro' },
    { key: 'system', icon: <DesktopOutlined />, label: 'Sistema' },
  ];

  return (
    <Dropdown
      menu={{
        items,
        selectable: true,
        selectedKeys: [mode],
        onClick: ({ key }) => setMode(key as ThemeMode),
      }}
      placement="bottomRight"
      trigger={['click']}
    >
      <Button
        type="text"
        icon={triggerIcon}
        aria-label="Alternar tema"
        title="Tema (claro/escuro/sistema)"
        style={{ height: '40px', width: '40px', fontSize: '16px' }}
      />
    </Dropdown>
  );
};

export default ThemeToggle;
