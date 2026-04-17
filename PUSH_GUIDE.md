# NeuroStride-VL Developer Guide
## How to Push to GitHub

### Prerequisites
1. You have a GitHub account
2. Git is installed
3. SSH keys or HTTPS credentials are configured

### Step 1: Configure Git User Info

```bash
cd ~/neurostride-vl

# Set your GitHub username and email
git config user.name "YourName"
git config user.email "your-email@example.com"
```

### Step 2: Configure Remote Repository

If the repository is yours (Chandan118/new), the remote should already be configured. Otherwise:

```bash
# Add remote repository (replace with your actual repo URL)
git remote add origin https://github.com/Chandan118/new.git
# Or use SSH:
# git remote add origin git@github.com:Chandan118/new.git
```

### Step 3: Push Code

```bash
# Push to GitHub
git push -u origin main

# If prompted for authentication:
# HTTPS: Enter GitHub username and Personal Access Token
# SSH: Ensure SSH key is added to GitHub and ssh-agent
```

### Create Personal Access Token (PAT)

If using HTTPS, you need to create a PAT:

1. Visit https://github.com/settings/tokens
2. Click "Generate new token"
3. Select permissions: `repo`, `workflow`
4. Generate token and copy it
5. Use this token as password when pushing

### Verify Push

Visit https://github.com/Chandan118/new to view code

### Next Steps

1. Create feature branches:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. Commit changes:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

3. Push and create PR:
   ```bash
   git push origin feature/amazing-feature
   ```

## Common Issues

**Q: Push fails with "Authentication failed"**

A: Check:
1. Use `git remote -v` to view remote URL
2. Ensure PAT has `repo` permission
3. Or switch to SSH: `git remote set-url origin git@github.com:...`

**Q: How to add collaborators?**

A: In GitHub repo page: Settings → Collaborators → Add people

**Q: How to protect main branch?**

A: Settings → Branches → Add rule → Require pull request reviews

## Project Structure

```
neurostride-vl/
├── src/                    # Source code
│   ├── env/               # MuJoCo environments
│   ├── agents/            # RL agents
│   ├── perception/        # Qwen-VL vision-language model
│   ├── ros2_bridge/       # ROS2 bridge nodes
│   └── utils/             # Utilities
├── configs/               # Configuration files
├── scripts/               # Install, train, deploy scripts
├── models/                # Model storage (.gitignore excludes)
├── docs/                  # Documentation
├── examples/              # Example code
└── tests/                 # Tests
```

## Next Actions

1. ✅ Push code to GitHub
2. 📖 Complete documentation (docs/)
3. 🚀 Train models on Mac M2 Pro
4. 📦 Quantize and deploy to Jetson Orin Nano
5. 🌟 Share project and get Stars!

Good luck!
