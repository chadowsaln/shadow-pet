// SHADIOS Life — walk, spider wall-climb, outfits, and multi-monitor roam.

const OUTFITS = ["outfit-royal", "outfit-dark"];
const SPIDER_CLIMB = "spider-climb";
const SPIDER_WALL = "spider-wall";

const SAFE_REACTIONS = ["idle", "waving", "success", "celebrating", "error"];

const SPEAKS = [
  "أنا SHADIOS ☁️",
  "يلا نتحرك!",
  "على الجدار!",
  "زاحف سحابي 🕷️",
  "شاشة جديدة!",
  "انميشن!",
];

function clampNumber(value, min, max, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.max(min, Math.min(max, Math.round(n)));
}

export function cleanConfig(raw = {}) {
  const c = raw && typeof raw === "object" ? raw : {};
  return {
    animations: c.animations !== false,
    outfits: c.outfits !== false,
    wallClimb: c.wallClimb !== false,
    animationIntervalMs: clampNumber(c.animationIntervalSec, 12, 180, 28) * 1000,
    outfitIntervalMs: clampNumber(c.outfitIntervalMin, 2, 60, 6) * 60 * 1000,
    outfitHoldMs: clampNumber(c.outfitHoldSec, 15, 180, 40) * 1000,
    climbIntervalMs: clampNumber(c.climbIntervalMin, 1, 30, 3) * 60 * 1000,
  };
}

function pick(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function register(OpenPetsPlugin) {
  let cleanup = () => {};

  OpenPetsPlugin.register({
    async start(ctx) {
      cleanup();
      let active = true;
      let cfg = cleanConfig(await ctx.config.get());
      let outfitIndex = 0;
      let wearingSprite = null;
      let busy = false;

      await ctx.status.set({ text: "SHADIOS alive", tone: "info" });

      async function setSprite(name, fps = 6) {
        await ctx.pet.setAnimation({ sprite: ctx.assets.sprite(name), loop: true, fps });
        wearingSprite = name;
      }

      async function clearSprite(reaction = "idle") {
        if (!wearingSprite) return;
        wearingSprite = null;
        try {
          await ctx.pet.setAnimation(reaction);
        } catch (err) {
          ctx.log.warn?.("clear sprite failed", err?.message);
        }
      }

      async function safeReact(reaction) {
        try {
          await ctx.pet.react(reaction, { showMessage: false });
        } catch (err) {
          ctx.log.warn?.("react failed", err?.message);
        }
      }

      async function maybeSpeak() {
        if (Math.random() < 0.2) {
          try {
            await ctx.pet.speak(pick(SPEAKS));
          } catch {
            /* ignore */
          }
        }
      }

      async function playAmbient() {
        if (!active || busy || wearingSprite) return;
        busy = true;
        try {
          await maybeSpeak();
        } finally {
          busy = false;
        }
      }

      async function applyOutfit() {
        if (!active || !cfg.outfits || busy) return;
        busy = true;
        try {
          const name = OUTFITS[outfitIndex % OUTFITS.length];
          outfitIndex += 1;
          await setSprite(name, 6);
          ctx.log.info?.("outfit applied", { name });
        } catch (err) {
          ctx.log.warn?.("outfit failed", err?.message);
        } finally {
          busy = false;
        }
      }

      async function clearOutfit() {
        if (wearingSprite === "outfit-royal" || wearingSprite === "outfit-dark") {
          await clearSprite("idle");
        }
      }

      async function getStateSafe() {
        try {
          return await ctx.pet.getState();
        } catch {
          return null;
        }
      }

      // Fire-and-forget moveBy with timed wait (SDK moveBy doesn't await completion)
      async function moveAbsWait(x, y, durationMs) {
        const s = await getStateSafe();
        if (!s || !s.position) return;
        const dx = Math.round(x - s.position.x);
        const dy = Math.round(y - s.position.y);
        if (Math.abs(dx) < 2 && Math.abs(dy) < 2) return;
        try {
          await ctx.pet.moveBy({ x: dx, y: dy, durationMs });
        } catch (err) {
          ctx.log.warn?.("moveBy failed", err?.message);
        }
        // Wait for move animation to finish before next action
        await sleep(durationMs + 200);
      }

      async function wallClimbSequence() {
        if (!active || busy || !cfg.wallClimb) return;
        if (wearingSprite && wearingSprite.startsWith("outfit-")) {
          await clearOutfit();
          await sleep(400);
        }
        busy = true;
        try {
          const state = await getStateSafe();
          if (!state || !state.visible) {
            busy = false;
            return;
          }

          const pos = state.position;
          const edges = [
            { name: "left", x: 4, y: pos.y },
            { name: "right", x: 1420, y: pos.y },
            { name: "top", x: pos.x, y: 4 },
            { name: "bottom", x: pos.x, y: 520 },
          ];
          const target = pick(edges);

          await setSprite(SPIDER_CLIMB, 8);
          await moveAbsWait(target.x, target.y, 1800);

          await setSprite(SPIDER_WALL, 9);
          const crossX = target.name === "left" ? 40 : 1280;
          const sideY = Math.max(20, Math.min(700, (target.y || 300) + (Math.random() < 0.5 ? -180 : 120)));
          await moveAbsWait(crossX, sideY, 2400);

          await setSprite(SPIDER_CLIMB, 8);
          const landX = Math.max(40, Math.min(1600, crossX + (Math.random() * 240 - 120)));
          const landY = Math.max(80, Math.min(600, sideY + 200));
          await moveAbsWait(landX, landY, 1600);

          await clearSprite("waving");
          await maybeSpeak();
          ctx.log.info?.("wall climb done", { target: target.name });
        } catch (err) {
          ctx.log.warn?.("wall climb failed", err?.message);
          await clearSprite("idle").catch(() => {});
        } finally {
          busy = false;
        }
      }

      let animationTimer = null;
      let outfitOnTimer = null;
      let outfitOffTimer = null;
      let climbTimer = null;

      function armAnimationLoop() {
        clearTimeout(animationTimer);
        if (!cfg.animations) return;
        const delay = cfg.animationIntervalMs * (0.65 + Math.random() * 0.7);
        animationTimer = setTimeout(async () => {
          if (!active) return;
          await playAmbient();
          armAnimationLoop();
        }, delay);
      }

      function armOutfitCycle() {
        clearTimeout(outfitOnTimer);
        clearTimeout(outfitOffTimer);
        if (!cfg.outfits) {
          clearOutfit().catch(() => {});
          return;
        }
        const delay = cfg.outfitIntervalMs * (0.7 + Math.random() * 0.6);
        outfitOnTimer = setTimeout(async () => {
          if (!active) return;
          await applyOutfit();
          outfitOffTimer = setTimeout(async () => {
            if (!active) return;
            await clearOutfit();
            armOutfitCycle();
          }, cfg.outfitHoldMs);
        }, delay);
      }

      function armClimbCycle() {
        clearTimeout(climbTimer);
        if (!cfg.wallClimb) return;
        const delay = cfg.climbIntervalMs * (0.65 + Math.random() * 0.7);
        climbTimer = setTimeout(async () => {
          if (!active) return;
          await wallClimbSequence();
          armClimbCycle();
        }, delay);
      }

      const unsubConfig = ctx.config.onChange(async (newRaw) => {
        if (!active) return;
        cfg = cleanConfig(newRaw);
        armAnimationLoop();
        armOutfitCycle();
        armClimbCycle();
      });

      armAnimationLoop();
      armOutfitCycle();
      armClimbCycle();

      cleanup = function stop() {
        active = false;
        clearTimeout(animationTimer);
        clearTimeout(outfitOnTimer);
        clearTimeout(outfitOffTimer);
        clearTimeout(climbTimer);
        unsubConfig();
        clearSprite("idle").catch(() => {});
        ctx.status.clear().catch(() => {});
      };
    },
    stop() {
      cleanup();
      cleanup = () => {};
    },
  });
}
