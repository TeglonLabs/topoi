# Tweag Pytest Automation Integration

To incorporate the Tweag pytest-automation-boilerplate into our topos project:

1. Clone the repository or add as a submodule.  
   Example (submodule):
   ```
   git submodule add https://github.com/tweag/pytest-automation-boilerplate.git \
   .topos/integrations/tweag-pytest-automation
   ```

2. Inspect the directory layout (tests folder, conftest.py) to adapt or merge with existing test structure.

3. Optionally unify any environment requirements (pytest plugins, fixtures) with the swirltrace or “just world” flows.  
   Combine with discopy or mealy machine testing patterns, ensuring all needed dependencies are installed.

4. Configure your CI (GitHub Actions, GitLab CI, etc.) to run tests from the newly integrated pytest boilerplate location.

Armenian Note: Տես այս ամենը որպես ալիքների շարժ, որտեղ թեստերը և hypergraph-ները միահյուսվում են:
(Translation: “See all this as a wave-like motion, where tests and hypergraphs interweave.”)

---

With this, you can leverage the boilerplate for automated testing, bridging the [pytest-automation-boilerplate](https://github.com/tweag/pytest-automation-boilerplate.git) approach with your existing swirl of monoidal and mealy-based logic.
