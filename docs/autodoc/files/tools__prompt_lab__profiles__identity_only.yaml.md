# tools/prompt_lab/profiles/identity_only.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 13

---

### File: tools/prompt_lab/profiles/identity_only.yaml

#### Purpose
This YAML file defines a profile named `identity_only` for the Mythos system, which specifies that only the identity layer should be active while all other layers are disabled. This profile is used to test the impact of the identity layer alone on the response.

#### Architecture
The file is structured as a simple YAML document with key-value pairs. It contains metadata and a set of boolean flags to enable or disable specific layers.

#### Patterns
No design patterns are applicable here as this is a configuration file and not part of the codebase.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is read by the Mythos system to configure the layers for a specific profile.

#### Interfaces
This file does not expose any interfaces. It is a configuration file that is consumed by the Mythos system to configure the layers for a specific profile.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that is used to configure the layers for a specific profile.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic here is the configuration of the layers. The `identity` layer is set to `true`, while all other layers (`personality`, `voice`, `mode`, `user_profile`, `dynamic_context`, `life_context`, `skills`) are set to `false`.

#### Integration Points
This file integrates with the Mythos system's prompt lab or similar subsystem that reads these profiles to configure the layers for generating responses. The `identity_only` profile is used to test the impact of the identity layer alone on the response.

### Detailed Breakdown

- **name**: `identity_only` - The name of the profile.
- **description**: `"Layer 1 only. Tests what identity alone does to the response."` - A description of the profile's purpose.
- **layers**: 
  - `identity: true` - Enables the identity layer.
  - `personality: false` - Disables the personality layer.
  - `voice: false` - Disables the voice layer.
  - `mode: false` - Disables the mode layer.
  - `user_profile: false` - Disables the user profile layer.
  - `dynamic_context: false` - Disables the dynamic context layer.
  - `life_context: false` - Disables the life context layer.
  - `skills: false` - Disables the skills layer.

This configuration file is used to isolate the identity layer's effect on the response, which can be useful for debugging and testing purposes within the Mythos system.
