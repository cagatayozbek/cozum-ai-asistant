"""
FAISS Query Test
İki farklı query ile retrieval kalitesini karşılaştır
"""

from retriever import get_retrieved_documents

print("="*80)
print("🧪 FAISS QUERY COMPARISON TEST")
print("="*80)

# Test 1: Kullanıcının orijinal sorusu
print("\n" + "="*80)
print("TEST 1: Kullanıcının Orijinal Sorusu")
print("="*80)
query1 = "eğitim programlarınız nelerdir"
print(f"📝 Query: '{query1}'")
print("-"*80)

results1 = get_retrieved_documents(
    query1,
    k=4,
    levels=["ortaokul"],
    force_recreate=False,
    silent=False  # Debug output göster
)

print(f"\n✅ {len(results1)} doküman bulundu")
for i, (doc, score) in enumerate(results1, 1):
    print(f"\n📄 Sonuç {i} | Score: {score:.4f}")
    print(f"   Level: {doc.metadata.get('level', 'N/A').upper()}")
    print(f"   Title: {doc.metadata.get('title', 'N/A')}")
    print(f"   Content: {doc.page_content[:150]}...")

# Test 2: LLM'in optimize ettiği query
print("\n\n" + "="*80)
print("TEST 2: LLM'in Optimize Ettiği Query")
print("="*80)
query2 = "eğitim programları"
print(f"📝 Query: '{query2}'")
print("-"*80)

results2 = get_retrieved_documents(
    query2,
    k=4,
    levels=["ortaokul"],
    force_recreate=False,
    silent=False  # Debug output göster
)

print(f"\n✅ {len(results2)} doküman bulundu")
for i, (doc, score) in enumerate(results2, 1):
    print(f"\n📄 Sonuç {i} | Score: {score:.4f}")
    print(f"   Level: {doc.metadata.get('level', 'N/A').upper()}")
    print(f"   Title: {doc.metadata.get('title', 'N/A')}")
    print(f"   Content: {doc.page_content[:150]}...")

# Karşılaştırma
print("\n\n" + "="*80)
print("📊 KARŞILAŞTIRMA")
print("="*80)

print(f"\nQuery 1: '{query1}'")
print(f"Query 2: '{query2}'")

print(f"\n🎯 Ortalama Score:")
avg_score1 = sum(score for _, score in results1) / len(results1) if results1 else 0
avg_score2 = sum(score for _, score in results2) / len(results2) if results2 else 0
print(f"   Query 1: {avg_score1:.4f}")
print(f"   Query 2: {avg_score2:.4f}")

if avg_score2 < avg_score1:
    print(f"\n✅ SONUÇ: LLM'in optimize ettiği query DAHA İYİ! (score: {avg_score2:.4f} < {avg_score1:.4f})")
    print("   Lower score = better match in FAISS")
elif avg_score2 > avg_score1:
    print(f"\n⚠️  SONUÇ: Orijinal query daha iyi! (score: {avg_score1:.4f} < {avg_score2:.4f})")
    print("   Lower score = better match in FAISS")
else:
    print(f"\n🟰 SONUÇ: İki query de eşit sonuç verdi (score: {avg_score1:.4f})")

# Aynı dokümanlar mı döndü?
doc_ids1 = {doc.metadata.get('id') for doc, _ in results1}
doc_ids2 = {doc.metadata.get('id') for doc, _ in results2}

if doc_ids1 == doc_ids2:
    print(f"\n📋 Aynı dokümanlar döndü ({len(doc_ids1)} doküman)")
else:
    print(f"\n📋 Farklı dokümanlar döndü:")
    print(f"   Sadece Query 1'de: {doc_ids1 - doc_ids2}")
    print(f"   Sadece Query 2'de: {doc_ids2 - doc_ids1}")
    print(f"   Ortak: {doc_ids1 & doc_ids2}")

print("\n" + "="*80)
