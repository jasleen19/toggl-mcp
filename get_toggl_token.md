# How to Get Your Toggl API Token

1. Log in to [Toggl Track](https://track.toggl.com)
2. Click on your profile picture (bottom left)
3. Select "Profile settings"
4. Scroll down to "API Token" section
5. Click "Click to reveal" or "Create new token"
6. Copy the token (it looks like a long string of letters and numbers)

## Finding Your Workspace ID

After setting up the MCP server, you can ask Claude:
- "Show me my Toggl workspaces"
- Note the workspace ID you want to use as default

## Security Tips

- Never commit your API token to git
- Store it in a password manager
- Use environment variables or Claude Desktop config only
